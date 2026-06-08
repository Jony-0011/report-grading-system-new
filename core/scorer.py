def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def calculate_structure_score(heading_result, max_score=10):
    try:
        max_score = safe_int(max_score, 10)
        if max_score <= 0:
            max_score = 10
        
        if not isinstance(heading_result, dict):
            return {'score': int(max_score * 0.2), 'reason': '输入数据格式错误'}
        
        total_ref = safe_int(heading_result.get('total_ref', 0))
        if total_ref == 0:
            return {'score': max_score, 'reason': '参考答案无标题信息'}
        
        similarity = safe_float(heading_result.get('similarity', 0.0))
        similarity = max(0.0, min(1.0, similarity))
        
        matched_count = safe_int(heading_result.get('matched', 0))
        matched_count = max(0, matched_count)
        
        total_ref = max(1, total_ref)
        extra = heading_result.get('extra', [])
        if not isinstance(extra, list):
            extra = []
        student_headings_count = len(extra) + matched_count
        
        if similarity >= 0.8:
            score = max_score
            reason = '章节结构完整，与参考答案一致'
        elif similarity >= 0.6:
            score = int(max_score * 0.85)
            reason = '章节基本完整'
        elif similarity >= 0.4:
            score = int(max_score * 0.7)
            reason = '章节结构较完整'
        elif student_headings_count >= 3:
            score = int(max_score * 0.6)
            reason = f'结构合理，包含{student_headings_count}个章节'
        elif student_headings_count >= 2:
            score = int(max_score * 0.5)
            reason = f'包含{student_headings_count}个基本章节'
        elif student_headings_count >= 1:
            score = int(max_score * 0.4)
            reason = '有基本章节结构'
        else:
            score = int(max_score * 0.2)
            reason = '章节结构较简单'
        
        return {'score': max(0, score), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.2), 'reason': f'计算错误: {str(e)[:30]}'}

def calculate_key_steps_score(keyword_result, max_score=30):
    try:
        max_score = safe_int(max_score, 30)
        if max_score <= 0:
            max_score = 30
        
        if not isinstance(keyword_result, dict):
            return {'score': int(max_score * 0.2), 'reason': '输入数据格式错误'}
        
        total_keywords = safe_int(keyword_result.get('total_keywords', 0))
        if total_keywords == 0:
            return {'score': max_score, 'reason': '无关键词配置'}
        
        accuracy = safe_float(keyword_result.get('accuracy', 0.0))
        accuracy = max(0.0, min(1.0, accuracy))
        
        details = keyword_result.get('details', [])
        if not isinstance(details, list):
            details = []
        
        matched = [r['keyword'] for r in details if isinstance(r, dict) and r.get('matched')]
        
        if accuracy >= 0.7:
            score = max_score
            reason = f'关键步骤完整，涵盖关键词: {\", \".join(matched)}'
        elif accuracy >= 0.5:
            score = int(max_score * 0.85)
            reason = f'关键步骤较完整，涵盖关键词: {\", \".join(matched)}'
        elif accuracy >= 0.3:
            score = int(max_score * 0.7)
            reason = f'关键步骤基本完整，涵盖关键词: {\", \".join(matched)}'
        elif accuracy >= 0.1:
            score = int(max_score * 0.5)
            reason = f'关键步骤部分完整，涵盖关键词: {\", \".join(matched)}'
        else:
            score = int(max_score * 0.2)
            reason = '关键步骤缺失较多'
        
        return {'score': max(0, score), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.2), 'reason': f'计算错误: {str(e)[:30]}'}

def calculate_result_score(text_result, max_score=25):
    try:
        max_score = safe_int(max_score, 25)
        if max_score <= 0:
            max_score = 25
        
        if not isinstance(text_result, dict):
            return {'score': int(max_score * 0.2), 'reason': '输入数据格式错误'}
        
        total_ref = safe_int(text_result.get('total_ref_words', 0))
        if total_ref == 0:
            return {'score': max_score, 'reason': '参考答案无文本内容'}
        
        similarity = safe_float(text_result.get('similarity', 0.0))
        similarity = max(0.0, min(1.0, similarity))
        
        common_words = safe_int(text_result.get('common_words', 0))
        common_words = max(0, common_words)
        
        if similarity >= 0.5:
            score = max_score
            reason = '内容匹配度高，与参考答案一致性好'
        elif similarity >= 0.3:
            score = int(max_score * 0.8)
            reason = '内容匹配度较好'
        elif similarity >= 0.15:
            score = int(max_score * 0.65)
            reason = '内容基本匹配'
        elif similarity >= 0.05:
            score = int(max_score * 0.5)
            reason = '内容有一定匹配度'
        elif common_words >= 3:
            score = int(max_score * 0.35)
            reason = '内容较少，但有相关内容'
        else:
            score = int(max_score * 0.2)
            reason = '内容较少，建议增加'
        
        return {'score': max(0, score), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.2), 'reason': f'计算错误: {str(e)[:30]}'}

def calculate_reflection_score(reflection_result, max_score=20):
    try:
        max_score = safe_int(max_score, 20)
        if max_score <= 0:
            max_score = 20
        
        if not isinstance(reflection_result, dict):
            return {'score': int(max_score * 0.35), 'reason': '输入数据格式错误'}
        
        found_keywords = reflection_result.get('found_keywords', [])
        if not isinstance(found_keywords, list):
            found_keywords = []
        
        found_count = len(found_keywords)
        
        if found_count >= 4:
            score = max_score
            keywords = \", \".join(found_keywords[:5])
            reason = f'反思内容丰富，提及关键词: {keywords}'
        elif found_count >= 2:
            score = int(max_score * 0.8)
            keywords = \", \".join(found_keywords[:5])
            reason = f'包含反思内容，提及关键词: {keywords}'
        elif found_count == 1:
            score = int(max_score * 0.55)
            reason = f'有少量反思内容，提及关键词: {found_keywords[0]}'
        else:
            score = int(max_score * 0.35)
            reason = '建议增加实训总结与反思内容'
        
        return {'score': max(0, min(score, max_score)), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.35), 'reason': f'计算错误: {str(e)[:30]}'}

def calculate_images_score(image_result, max_score=10):
    try:
        max_score = safe_int(max_score, 10)
        if max_score <= 0:
            max_score = 10
        
        if not isinstance(image_result, dict):
            return {'score': int(max_score * 0.3), 'reason': '输入数据格式错误'}
        
        ref_count = safe_int(image_result.get('ref_count', 0))
        student_count = safe_int(image_result.get('student_count', 0))
        
        ref_count = max(0, ref_count)
        student_count = max(0, student_count)
        
        if ref_count == 0:
            return {'score': max_score, 'reason': '参考答案无图片要求'}
        
        ratio = safe_float(image_result.get('ratio', 0.0))
        if ratio <= 0:
            ratio = student_count / ref_count if ref_count > 0 else 0.0
        ratio = max(0.0, ratio)
        
        if ratio >= 1.0:
            score = max_score
            reason = f'图片数量充足 ({student_count}/{ref_count})'
        elif ratio >= 0.8:
            score = int(max_score * 0.8)
            reason = f'图片数量略少 ({student_count}/{ref_count})'
        elif ratio >= 0.5:
            score = int(max_score * 0.6)
            reason = f'图片数量不足 ({student_count}/{ref_count})'
        else:
            score = int(max_score * 0.3)
            reason = f'图片数量较少 ({student_count}/{ref_count})'
        
        return {'score': max(0, score), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.3), 'reason': f'计算错误: {str(e)[:30]}'}

def calculate_format_score(format_result, max_score=5):
    try:
        max_score = safe_int(max_score, 5)
        if max_score <= 0:
            max_score = 5
        
        if not isinstance(format_result, dict):
            return {'score': int(max_score * 0.8), 'reason': '输入数据格式错误'}
        
        proper_format = format_result.get('proper_format', False)
        
        if proper_format:
            score = max_score
            reason = '格式规范，排版良好'
        else:
            score = int(max_score * 0.8)
            reason = '格式基本规范'
        
        return {'score': max(0, score), 'reason': reason}
    except Exception as e:
        return {'score': int(max_score * 0.8), 'reason': f'计算错误: {str(e)[:30]}'}

def generate_comment(scores, comparison_details):
    try:
        if not isinstance(scores, dict):
            return '评分数据格式错误，无法生成评语。'
        
        total_score = 0
        for s in scores.values():
            if isinstance(s, dict) and 'score' in s:
                total_score += safe_int(s.get('score', 0))
        
        comments = []
        
        if total_score >= 90:
            comments.append('本报告完成出色，各方面表现优秀。')
        elif total_score >= 80:
            comments.append('本报告完成良好，整体质量较高。')
        elif total_score >= 70:
            comments.append('本报告完成较好，继续努力。')
        elif total_score >= 60:
            comments.append('本报告基本合格，存在一些需要改进的地方。')
        else:
            comments.append('本报告需要认真修改完善。')
        
        if isinstance(scores, dict):
            low_scores = [(k, v) for k, v in scores.items() 
                         if isinstance(v, dict) and safe_int(v.get('score', 0)) < safe_int(v.get('max_score', 100)) * 0.6]
            category_names = {
                'structure': '结构完整性',
                'key_steps': '关键步骤',
                'result': '结果匹配',
                'reflection': '反思总结',
                'images': '图片数量',
                'format': '格式规范'
            }
            for category, score_info in low_scores:
                if isinstance(score_info, dict) and 'reason' in score_info:
                    comments.append(f'{category_names.get(category, category)}方面需要加强: {score_info["reason"]}')
        
        if isinstance(comparison_details, dict):
            if comparison_details.get('heading_result') and comparison_details['heading_result'].get('missing'):
                missing = comparison_details['heading_result']['missing'][:3]
                if isinstance(missing, list):
                    comments.append(f'建议补充以下章节: {\", \".join(missing)}')
            
            if comparison_details.get('reflection_result') and not comparison_details['reflection_result'].get('has_reflection'):
                comments.append('建议增加实训总结与反思部分，包括收获体会和改进方向。')
            
            if comparison_details.get('image_result'):
                img_ratio = safe_float(comparison_details['image_result'].get('ratio', 0.0))
                if img_ratio < 0.8:
                    comments.append('建议适当增加图片数量以丰富报告内容。')
        
        comments.append('继续努力，不断提高报告质量！')
        
        return '\n\n'.join(comments)
    except Exception as e:
        return f'评语生成错误: {str(e)[:50]}'

def get_grade(total_score):
    try:
        total_score = safe_int(total_score, 0)
        total_score = max(0, min(100, total_score))
        
        if total_score >= 84:
            return '优秀'
        elif total_score >= 75:
            return '良好'
        elif total_score >= 65:
            return '中等'
        elif total_score >= 60:
            return '及格'
        else:
            return '不及格'
    except Exception as e:
        return '不及格'

def calculate_total_score(scores):
    try:
        if not isinstance(scores, dict):
            return 0
        
        total = 0
        for s in scores.values():
            if isinstance(s, dict) and 'score' in s:
                total += safe_int(s.get('score', 0))
        
        return max(0, total)
    except Exception as e:
        return 0

if __name__ == '__main__':
    import unittest
    
    class TestGradingUnit(unittest.TestCase):
        
        def test_get_grade_boundary_cases(self):
            self.assertEqual(get_grade(84), '优秀')
            self.assertEqual(get_grade(83), '良好')
            self.assertEqual(get_grade(75), '良好')
            self.assertEqual(get_grade(74), '中等')
            self.assertEqual(get_grade(65), '中等')
            self.assertEqual(get_grade(64), '及格')
            self.assertEqual(get_grade(60), '及格')
            self.assertEqual(get_grade(59), '不及格')
            
        def test_get_grade_extreme_cases(self):
            self.assertEqual(get_grade(100), '优秀')
            self.assertEqual(get_grade(0), '不及格')
            self.assertEqual(get_grade(50), '不及格')
            self.assertEqual(get_grade(95), '优秀')
            
        def test_get_grade_invalid_inputs(self):
            self.assertEqual(get_grade(-10), '不及格')
            self.assertEqual(get_grade('invalid'), '不及格')
            self.assertEqual(get_grade(None), '不及格')
            self.assertEqual(get_grade(150), '优秀')
            
        def test_calculate_structure_score(self):
            heading_result = {
                'matched': 8,
                'total_ref': 8,
                'similarity': 1.0,
                'missing': [],
                'extra': []
            }
            result = calculate_structure_score(heading_result, 10)
            self.assertEqual(result['score'], 10)
            
            heading_result_low = {
                'matched': 1,
                'total_ref': 8,
                'similarity': 0.125,
                'missing': ['a', 'b', 'c'],
                'extra': []
            }
            result = calculate_structure_score(heading_result_low, 10)
            self.assertEqual(result['score'], 4)
            
        def test_calculate_structure_score_invalid(self):
            result = calculate_structure_score(None, 10)
            self.assertEqual(result['score'], 2)
            
            result = calculate_structure_score('invalid', 10)
            self.assertEqual(result['score'], 2)
            
            result = calculate_structure_score({'similarity': -1, 'matched': -5}, 10)
            self.assertTrue(result['score'] >= 0)
            
        def test_calculate_key_steps_score(self):
            keyword_result = {
                'details': [{'keyword': 'test', 'matched': True}],
                'matched_count': 1,
                'total_keywords': 1,
                'accuracy': 1.0
            }
            result = calculate_key_steps_score(keyword_result, 30)
            self.assertEqual(result['score'], 30)
            
        def test_calculate_result_score(self):
            text_result = {
                'common_words': 50,
                'total_ref_words': 100,
                'similarity': 0.5
            }
            result = calculate_result_score(text_result, 25)
            self.assertEqual(result['score'], 25)
            
        def test_calculate_reflection_score(self):
            reflection_result = {
                'has_reflection': True,
                'found_keywords': ['总结', '反思', '收获', '改进'],
                'score': 0.33
            }
            result = calculate_reflection_score(reflection_result, 20)
            self.assertEqual(result['score'], 20)
            
        def test_calculate_images_score(self):
            image_result = {
                'ref_count': 5,
                'student_count': 5,
                'ratio': 1.0
            }
            result = calculate_images_score(image_result, 10)
            self.assertEqual(result['score'], 10)
            
        def test_calculate_format_score(self):
            format_result = {'proper_format': True}
            result = calculate_format_score(format_result, 5)
            self.assertEqual(result['score'], 5)
            
            format_result_false = {'proper_format': False}
            result = calculate_format_score(format_result_false, 5)
            self.assertEqual(result['score'], 4)
            
        def test_calculate_total_score(self):
            scores = {
                'structure': {'score': 8},
                'key_steps': {'score': 30},
                'result': {'score': 20},
                'reflection': {'score': 16},
                'images': {'score': 10},
                'format': {'score': 4}
            }
            total = calculate_total_score(scores)
            self.assertEqual(total, 88)
            
        def test_calculate_total_score_invalid(self):
            self.assertEqual(calculate_total_score(None), 0)
            self.assertEqual(calculate_total_score('invalid'), 0)
            self.assertEqual(calculate_total_score({'a': 'b'}), 0)
    
    unittest.main(verbosity=2)