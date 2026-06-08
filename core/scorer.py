def calculate_structure_score(heading_result, max_score=10):
    if heading_result['total_ref'] == 0:
        return {'score': max_score, 'reason': '参考答案无标题信息'}
    
    similarity = heading_result['similarity']
    missing = heading_result['missing']
    
    if similarity >= 0.9:
        score = max_score
        reason = '章节结构完整，与参考答案一致'
    elif similarity >= 0.7:
        score = int(max_score * 0.8)
        reason = f'章节基本完整，缺少少量标题: {", ".join(missing[:3])}' if missing else '章节基本完整'
    elif similarity >= 0.5:
        score = int(max_score * 0.5)
        reason = f'章节结构不完整，缺少部分标题: {", ".join(missing[:5])}'
    else:
        score = int(max_score * 0.2)
        reason = f'章节结构严重缺失，缺少多个关键标题: {", ".join(missing[:5])}'
    
    return {'score': score, 'reason': reason}

def calculate_key_steps_score(keyword_result, max_score=30):
    if keyword_result['total_keywords'] == 0:
        return {'score': max_score, 'reason': '无关键词配置'}
    
    accuracy = keyword_result['accuracy']
    missed = [r['keyword'] for r in keyword_result['details'] if not r['matched']]
    
    if accuracy >= 0.9:
        score = max_score
        reason = '关键步骤完整，所有关键词均已涵盖'
    elif accuracy >= 0.7:
        score = int(max_score * 0.8)
        reason = f'关键步骤基本完整，少量关键词缺失: {", ".join(missed[:3])}'
    elif accuracy >= 0.5:
        score = int(max_score * 0.5)
        reason = f'关键步骤不完整，部分关键词缺失: {", ".join(missed[:5])}'
    else:
        score = int(max_score * 0.2)
        reason = f'关键步骤严重缺失，多个关键词未涵盖: {", ".join(missed[:5])}'
    
    return {'score': score, 'reason': reason}

def calculate_result_score(text_result, max_score=25):
    similarity = text_result['similarity']
    
    if similarity >= 0.8:
        score = max_score
        reason = '内容匹配度高，与参考答案一致性好'
    elif similarity >= 0.6:
        score = int(max_score * 0.8)
        reason = '内容匹配度较好，大部分内容一致'
    elif similarity >= 0.4:
        score = int(max_score * 0.5)
        reason = '内容匹配度一般，部分内容需要完善'
    else:
        score = int(max_score * 0.2)
        reason = '内容匹配度较低，需参考参考答案补充'
    
    return {'score': score, 'reason': reason}

def calculate_reflection_score(reflection_result, max_score=20):
    if reflection_result['has_reflection']:
        score = int(max_score * (0.7 + reflection_result['score'] * 0.3))
        keywords = ", ".join(reflection_result['found_keywords'])
        reason = f'包含反思内容，提及关键词: {keywords}'
    else:
        score = int(max_score * 0.3)
        reason = '缺少反思总结部分，建议增加实训体会和改进方向'
    
    return {'score': min(score, max_score), 'reason': reason}

def calculate_images_score(image_result, max_score=10):
    if image_result['ref_count'] == 0:
        return {'score': max_score, 'reason': '参考答案无图片要求'}
    
    ratio = image_result['ratio']
    
    if ratio >= 1.0:
        score = max_score
        reason = f'图片数量充足 ({image_result["student_count"]}/{image_result["ref_count"]})'
    elif ratio >= 0.8:
        score = int(max_score * 0.8)
        reason = f'图片数量略少 ({image_result["student_count"]}/{image_result["ref_count"]})'
    elif ratio >= 0.5:
        score = int(max_score * 0.5)
        reason = f'图片数量不足 ({image_result["student_count"]}/{image_result["ref_count"]})'
    else:
        score = int(max_score * 0.2)
        reason = f'图片数量严重不足 ({image_result["student_count"]}/{image_result["ref_count"]})'
    
    return {'score': score, 'reason': reason}

def calculate_format_score(format_result, max_score=5):
    if format_result['proper_format']:
        score = max_score
        reason = '格式规范，排版良好'
    else:
        score = int(max_score * 0.5)
        reason = '格式不够规范，建议检查排版'
    
    return {'score': score, 'reason': reason}

def generate_comment(scores, comparison_details):
    total_score = sum(s['score'] for s in scores.values())
    comments = []
    
    if total_score >= 90:
        comments.append('本报告完成出色，各方面表现优秀。')
    elif total_score >= 80:
        comments.append('本报告完成良好，整体质量较高。')
    elif total_score >= 60:
        comments.append('本报告基本合格，存在一些需要改进的地方。')
    else:
        comments.append('本报告需要认真修改完善。')
    
    low_scores = [(k, v) for k, v in scores.items() if v['score'] < v.get('max_score', 100) * 0.6]
    for category, score_info in low_scores:
        category_names = {
            'structure': '结构完整性',
            'key_steps': '关键步骤',
            'result': '结果匹配',
            'reflection': '反思总结',
            'images': '图片数量',
            'format': '格式规范'
        }
        comments.append(f'{category_names.get(category, category)}方面需要加强: {score_info["reason"]}')
    
    if comparison_details.get('heading_result') and comparison_details['heading_result']['missing']:
        missing = comparison_details['heading_result']['missing'][:3]
        comments.append(f'建议补充以下章节: {", ".join(missing)}')
    
    if comparison_details.get('reflection_result') and not comparison_details['reflection_result']['has_reflection']:
        comments.append('建议增加实训总结与反思部分，包括收获体会和改进方向。')
    
    if comparison_details.get('image_result'):
        img_ratio = comparison_details['image_result']['ratio']
        if img_ratio < 0.8:
            comments.append('建议适当增加图片数量以丰富报告内容。')
    
    comments.append('继续努力，不断提高报告质量！')
    
    return '\n\n'.join(comments)

def get_grade(total_score):
    if total_score >= 90:
        return '优秀'
    elif total_score >= 80:
        return '良好'
    elif total_score >= 60:
        return '及格'
    else:
        return '不及格'

def calculate_total_score(scores):
    return sum(s['score'] for s in scores.values())