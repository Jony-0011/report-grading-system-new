import streamlit as st
import os
import tempfile
import json
import hashlib
import re

from core.parser import parse_document
from core.comparator import (
    compare_headings, compare_keywords, compare_text_content,
    compare_images, detect_reflection, check_format
)
from core.scorer import (
    calculate_structure_score, calculate_key_steps_score,
    calculate_result_score, calculate_reflection_score,
    calculate_images_score, calculate_format_score,
    generate_comment, get_grade, calculate_total_score
)
from utils.file_handler import process_uploaded_files, get_file_type
from utils.exporter import export_to_json, export_to_html

# ==================== 用户认证相关函数 ====================
USERS_FILE = "users.json"

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """保存用户数据"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def encrypt_password(password):
    """简单的密码加密（MD5）"""
    return hashlib.md5(password.encode()).hexdigest()

def validate_phone(phone):
    """校验手机号格式（11位数字，以1开头）"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def show_login_page():
    """显示登录注册页面"""
    st.set_page_config(
        page_title="实训报告智能批改系统 - 登录",
        page_icon="📝",
        layout="centered"
    )
    
    # 自定义样式
    st.markdown("""
    <style>
    .login-box {
        max-width: 420px;
        margin: 0 auto;
        padding: 30px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .main-title {
        color: #1e3a5f;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 8px;
    }
    .sub-title {
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        border: none;
        margin-top: 10px;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
    .tab-content {
        padding: 10px 0;
    }
    .input-label {
        font-weight: 500;
        color: #333;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 主标题区域
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 class="main-title">实训报告智能批改系统</h1>
        <p class="sub-title">登录系统开始批改工作</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 登录框
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    # 创建选项卡
    tab1, tab2 = st.tabs(["用户登录", "手机号注册"])
    
    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        
        phone = st.text_input("手机号", placeholder="请输入您的手机号", key="login_phone")
        password = st.text_input("密码", placeholder="请输入密码", type="password", key="login_pwd")
        
        if st.button("登 录", key="login_btn"):
            users = load_users()
            
            if not phone:
                st.error("请输入手机号")
            elif not validate_phone(phone):
                st.error("请输入正确的手机号格式（11位数字）")
            elif not password:
                st.error("请输入密码")
            elif phone not in users:
                st.error("账号不存在，请先注册")
            elif users[phone] != encrypt_password(password):
                st.error("密码错误，请重试")
            else:
                # 登录成功，初始化必要的会话状态
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = phone
                st.session_state['ref_answer'] = None
                st.session_state['ref_data'] = None
                st.session_state['student_reports'] = []
                st.session_state['grading_results'] = []
                st.success("登录成功！正在进入系统...")
                # 使用 rerun 确保页面正确跳转
                try:
                    st.rerun()
                except:
                    st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        
        phone = st.text_input("手机号", placeholder="请输入您的手机号", key="reg_phone")
        password = st.text_input("密码", placeholder="请设置密码（6-16位）", type="password", key="reg_pwd")
        confirm_pwd = st.text_input("确认密码", placeholder="请再次输入密码", type="password", key="reg_confirm_pwd")
        
        if st.button("注 册", key="reg_btn"):
            users = load_users()
            
            if not phone:
                st.error("请输入手机号")
            elif not validate_phone(phone):
                st.error("请输入正确的手机号格式（11位数字）")
            elif phone in users:
                st.error("该手机号已注册，请直接登录")
            elif not password:
                st.error("请设置密码")
            elif len(password) < 6 or len(password) > 16:
                st.error("密码长度需在6-16位之间")
            elif password != confirm_pwd:
                st.error("两次输入的密码不一致")
            else:
                # 注册成功
                users[phone] = encrypt_password(password)
                save_users(users)
                st.success("注册成功！请登录")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部提示
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 14px;">
        <p>提示：首次使用请先注册账号</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== 原有系统相关函数 ====================
def init_session_state():
    if 'ref_answer' not in st.session_state:
        st.session_state.ref_answer = None
    if 'ref_data' not in st.session_state:
        st.session_state.ref_data = None
    if 'weights' not in st.session_state:
        st.session_state.weights = {
            'structure': 10,
            'key_steps': 30,
            'result': 25,
            'reflection': 20,
            'images': 10,
            'format': 5
        }
    if 'student_reports' not in st.session_state:
        st.session_state.student_reports = []
    if 'grading_results' not in st.session_state:
        st.session_state.grading_results = []
    if 'selected_report' not in st.session_state:
        st.session_state.selected_report = None

def grade_report(student_data, ref_data, weights):
    heading_result = compare_headings(ref_data.get('headings', []), student_data.get('headings', []))
    
    keywords = ['引言', '目的', '步骤', '方法', '结果', '分析', '结论', '总结']
    keyword_result = compare_keywords(ref_data.get('text', ''), student_data.get('text', ''), keywords)
    
    text_result = compare_text_content(ref_data.get('text', ''), student_data.get('text', ''))
    
    image_result = compare_images(ref_data.get('images_count', 0), student_data.get('images_count', 0))
    
    reflection_result = detect_reflection(student_data.get('text', ''))
    
    format_result = check_format(student_data.get('text', ''))
    
    scores = {
        'structure': calculate_structure_score(heading_result, max_score=weights['structure']),
        'key_steps': calculate_key_steps_score(keyword_result, max_score=weights['key_steps']),
        'result': calculate_result_score(text_result, max_score=weights['result']),
        'reflection': calculate_reflection_score(reflection_result, max_score=weights['reflection']),
        'images': calculate_images_score(image_result, max_score=weights['images']),
        'format': calculate_format_score(format_result, max_score=weights['format'])
    }
    
    for key in scores:
        scores[key]['max_score'] = weights[key]
    
    comparison_details = {
        'heading_result': heading_result,
        'keyword_result': keyword_result,
        'text_result': text_result,
        'image_result': image_result,
        'reflection_result': reflection_result,
        'format_result': format_result
    }
    
    total_score = calculate_total_score(scores)
    grade = get_grade(total_score)
    comment = generate_comment(scores, comparison_details)
    
    return {
        'scores': scores,
        'total_score': total_score,
        'grade': grade,
        'comment': comment,
        'comparison_details': comparison_details
    }

def show_main_system():
    """显示主系统页面"""
    init_session_state()
    
    st.set_page_config(
        page_title="实训报告智能批改系统",
        page_icon="📝",
        layout="wide"
    )
    
    with st.sidebar:
        st.header("系统设置")
        
        # 显示当前用户
        st.markdown(f"**当前用户:** {st.session_state['current_user']}")
        
        # 退出登录按钮
        if st.button("退出登录"):
            # 清理所有会话状态
            st.session_state['logged_in'] = False
            st.session_state['current_user'] = None
            st.session_state['ref_answer'] = None
            st.session_state['ref_data'] = None
            st.session_state['student_reports'] = []
            st.session_state['grading_results'] = []
            st.session_state['selected_report'] = None
            # 使用 rerun 确保页面正确跳转
            try:
                st.rerun()
            except:
                st.experimental_rerun()
        
        st.markdown("---")
        
        st.subheader("参考答案报告")
        ref_file = st.file_uploader("上传参考答案 (docx)", type=['docx'], key='ref_uploader')
        
        if ref_file:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as f:
                    f.write(ref_file.getbuffer())
                    temp_path = f.name
                
                st.session_state.ref_data = parse_document(temp_path, 'docx')
                st.session_state.ref_answer = ref_file.name
                os.unlink(temp_path)
                st.success(f"已加载: {ref_file.name}")
            except Exception as e:
                st.error(f"加载失败: {str(e)}")
        
        st.subheader("评分权重配置")
        st.session_state.weights['structure'] = st.slider("结构完整性", 0, 20, st.session_state.weights['structure'])
        st.session_state.weights['key_steps'] = st.slider("关键步骤", 0, 40, st.session_state.weights['key_steps'])
        st.session_state.weights['result'] = st.slider("结果匹配", 0, 30, st.session_state.weights['result'])
        st.session_state.weights['reflection'] = st.slider("反思总结", 0, 25, st.session_state.weights['reflection'])
        st.session_state.weights['images'] = st.slider("图片数量", 0, 15, st.session_state.weights['images'])
        st.session_state.weights['format'] = st.slider("格式规范", 0, 10, st.session_state.weights['format'])
        
        total_weight = sum(st.session_state.weights.values())
        if total_weight != 100:
            st.warning(f"权重总和: {total_weight}% (建议调整为100%)")
        else:
            st.info("权重总和: 100% ✓")
        
        if st.button("重置设置"):
            st.session_state.ref_answer = None
            st.session_state.ref_data = None
            st.session_state.weights = {
                'structure': 10,
                'key_steps': 30,
                'result': 25,
                'reflection': 20,
                'images': 10,
                'format': 5
            }
            st.session_state.student_reports = []
            st.session_state.grading_results = []
            st.session_state.selected_report = None
            st.success("已重置所有设置")
    
    st.title("实训报告智能批改系统")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("学生报告上传")
        student_files = st.file_uploader(
            "批量上传学生报告 (docx/pdf)",
            type=['docx', 'pdf'],
            accept_multiple_files=True,
            key='student_uploader'
        )
        
        if student_files:
            st.session_state.student_reports = process_uploaded_files(student_files)
    
    with col2:
        st.header("开始批改")
        if st.button("开始批改", use_container_width=True):
            if not st.session_state.ref_data:
                st.error("请先上传参考答案报告！")
            elif not st.session_state.student_reports:
                st.error("请先上传学生报告！")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                st.session_state.grading_results = []
                total = len(st.session_state.student_reports)
                
                for i, report in enumerate(st.session_state.student_reports):
                    if report['success']:
                        result = grade_report(report['data'], st.session_state.ref_data, st.session_state.weights)
                        result['file_name'] = report['name']
                        st.session_state.grading_results.append(result)
                    
                    progress = (i + 1) / total
                    progress_bar.progress(progress)
                    status_text.text(f"正在批改: {i + 1}/{total}")
                
                status_text.text("批改完成！")
                st.success(f"已完成 {len(st.session_state.grading_results)} 份报告的批改")
    
    st.markdown("---")
    
    st.header("批改结果列表")
    if st.session_state.grading_results:
        results_df = [
            {
                '文件名': r['file_name'],
                '总分': r['total_score'],
                '评级': r['grade'],
                '状态': '已完成'
            }
            for r in st.session_state.grading_results
        ]
        
        st.dataframe(results_df, use_container_width=True)
        
        selected_name = st.selectbox(
            "选择报告查看详情",
            [r['file_name'] for r in st.session_state.grading_results],
            key='report_selector'
        )
        
        selected_result = next(r for r in st.session_state.grading_results if r['file_name'] == selected_name)
        
        st.markdown("---")
        st.subheader(f"报告详情: {selected_name}")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("总分", selected_result['total_score'], f"评级: {selected_result['grade']}")
        with info_col2:
            grade_color = {
                '优秀': 'green',
                '良好': 'blue',
                '中等': 'orange',
                '及格': 'orange',
                '不及格': 'red'
            }[selected_result['grade']]
            st.markdown(f"<span style='color:{grade_color};font-size:24px;font-weight:bold;'>{selected_result['grade']}</span>", unsafe_allow_html=True)
        with info_col3:
            st.write("")
        
        st.subheader("分项得分")
        score_cols = st.columns(3)
        category_names = {
            'structure': '结构完整性',
            'key_steps': '关键步骤',
            'result': '结果匹配',
            'reflection': '反思总结',
            'images': '图片数量',
            'format': '格式规范'
        }
        
        for i, (key, score_info) in enumerate(selected_result['scores'].items()):
            with score_cols[i % 3]:
                with st.expander(f"{category_names[key]}"):
                    st.write(f"得分: **{score_info['score']}** / {score_info['max_score']}")
                    st.write(f"扣分原因: {score_info['reason']}")
        
        st.subheader("差异比对")
        details = selected_result['comparison_details']
        
        with st.expander("章节结构比对"):
            if details['heading_result']['missing']:
                st.markdown("**缺失章节:**")
                for item in details['heading_result']['missing']:
                    st.markdown(f"- <span style='color:red'>{item}</span>", unsafe_allow_html=True)
            if details['heading_result']['extra']:
                st.markdown("**额外章节:**")
                for item in details['heading_result']['extra']:
                    st.markdown(f"- <span style='color:green'>{item}</span>", unsafe_allow_html=True)
            st.write(f"匹配度: {int(details['heading_result']['similarity'] * 100)}%")
        
        with st.expander("关键词匹配"):
            for kw in details['keyword_result']['details']:
                color = 'green' if kw['matched'] else 'red'
                st.markdown(f"- <span style='color:{color}'>{kw['keyword']}</span>: 参考答案 {kw['ref_count']}次 | 学生 {kw['student_count']}次", unsafe_allow_html=True)
        
        with st.expander("图片数量比对"):
            ref_count = details['image_result']['ref_count']
            stu_count = details['image_result']['student_count']
            st.write(f"参考答案图片数: {ref_count}")
            st.write(f"学生报告图片数: {stu_count}")
            if stu_count >= ref_count:
                st.success(f"图片数量充足")
            else:
                st.warning(f"图片数量不足，建议补充 {ref_count - stu_count} 张图片")
        
        st.subheader("教师评语")
        st.write(selected_result['comment'])
        
        st.subheader("导出报告")
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            json_data = export_to_json([selected_result])
            st.download_button(
                "导出 JSON",
                data=json_data,
                file_name=f"{selected_name}_批改结果.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_export2:
            html_data = export_to_html([selected_result])
            st.download_button(
                "导出 HTML",
                data=html_data,
                file_name=f"{selected_name}_批改结果.html",
                mime="text/html",
                use_container_width=True
            )
        
        if len(st.session_state.grading_results) > 1:
            st.subheader("批量导出")
            col_batch1, col_batch2 = st.columns(2)
            
            with col_batch1:
                all_json = export_to_json(st.session_state.grading_results)
                st.download_button(
                    "全部导出 JSON",
                    data=all_json,
                    file_name="所有报告批改结果.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_batch2:
                all_html = export_to_html(st.session_state.grading_results)
                st.download_button(
                    "全部导出 HTML",
                    data=all_html,
                    file_name="所有报告批改结果.html",
                    mime="text/html",
                    use_container_width=True
                )
    else:
        st.info("请上传学生报告并点击开始批改按钮")

# ==================== 主入口函数 ====================
def main():
    # 初始化登录状态
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        # 已登录，显示主系统
        show_main_system()
    else:
        # 未登录，显示登录页面
        show_login_page()

if __name__ == "__main__":
    main()