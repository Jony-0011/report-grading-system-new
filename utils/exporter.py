import json
import html

def export_to_json(grading_results):
    data = []
    
    for result in grading_results:
        item = {
            'file_name': result['file_name'],
            'total_score': result['total_score'],
            'grade': result['grade'],
            'scores': result['scores'],
            'comment': result['comment'],
            'comparison_details': result.get('comparison_details', {})
        }
        data.append(item)
    
    return json.dumps(data, ensure_ascii=False, indent=2)

def export_to_html(grading_results):
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>实训报告批改结果</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .report-card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
        .file-name { font-size: 18px; font-weight: bold; color: #333; }
        .score-badge { font-size: 24px; font-weight: bold; padding: 5px 15px; border-radius: 20px; }
        .score-badge.excellent { background: #28a745; color: white; }
        .score-badge.good { background: #17a2b8; color: white; }
        .score-badge.pass { background: #ffc107; color: #333; }
        .score-badge.fail { background: #dc3545; color: white; }
        .grade { margin-left: 10px; font-size: 16px; }
        .scores-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .score-item { padding: 12px; border-radius: 8px; background: #f8f9fa; }
        .score-item h4 { margin-bottom: 5px; color: #495057; }
        .score-value { font-size: 20px; font-weight: bold; color: #667eea; }
        .score-max { color: #999; }
        .reason { font-size: 12px; color: #666; margin-top: 5px; }
        .comment-section { background: #e7f3ff; padding: 15px; border-radius: 8px; }
        .comment-section h3 { color: #0c63e4; margin-bottom: 10px; }
        .comment-text { line-height: 1.6; color: #333; }
        .footer { text-align: center; color: #999; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>实训报告智能批改系统</h1>
            <p>共批改 {total_count} 份报告</p>
        </div>
        {report_cards}
        <div class="footer">
            <p>© 2024 实训报告智能批改系统 | 离线版</p>
        </div>
    </div>
</body>
</html>"""
    
    report_cards = []
    
    for result in grading_results:
        grade_class = {
            '优秀': 'excellent',
            '良好': 'good',
            '及格': 'pass',
            '不及格': 'fail'
        }.get(result['grade'], 'pass')
        
        scores_html = ''
        for category, score_info in result['scores'].items():
            category_names = {
                'structure': '结构完整性',
                'key_steps': '关键步骤',
                'result': '结果匹配',
                'reflection': '反思总结',
                'images': '图片数量',
                'format': '格式规范'
            }
            scores_html += """
<div class="score-item">
    <h4>{category_name}</h4>
    <span class="score-value">{score}</span>
    <span class="score-max">/{max_score}</span>
    <div class="reason">{reason}</div>
</div>""".format(
                category_name=category_names.get(category, category),
                score=score_info['score'],
                max_score=score_info.get('max_score', 100),
                reason=html.escape(score_info['reason'])
            )
        
        escaped_comment = html.escape(result['comment']).replace('\n', '<br>')
        card = """
<div class="report-card">
    <div class="card-header">
        <span class="file-name">{file_name}</span>
        <div>
            <span class="score-badge {grade_class}">{total_score}</span>
            <span class="grade">{grade}</span>
        </div>
    </div>
    <div class="scores-grid">
        {scores_html}
    </div>
    <div class="comment-section">
        <h3>教师评语</h3>
        <div class="comment-text">{comment}</div>
    </div>
</div>""".format(
            file_name=html.escape(result['file_name']),
            grade_class=grade_class,
            total_score=result['total_score'],
            grade=result['grade'],
            scores_html=scores_html,
            comment=escaped_comment
        )
        
        report_cards.append(card)
    
    return html_content.format(
        total_count=len(grading_results),
        report_cards='\n'.join(report_cards)
    )