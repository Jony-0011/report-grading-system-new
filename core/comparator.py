import re
from collections import Counter

def compare_headings(ref_headings, student_headings):
    matched = 0
    missing = []
    extra = []
    
    ref_lower = [h.lower().strip() for h in ref_headings]
    student_lower = [h.lower().strip() for h in student_headings]
    
    for ref_h in ref_lower:
        if ref_h in student_lower:
            matched += 1
        else:
            missing.append(ref_h)
    
    for student_h in student_lower:
        if student_h not in ref_lower:
            extra.append(student_h)
    
    return {
        'matched': matched,
        'total_ref': len(ref_headings),
        'missing': missing,
        'extra': extra,
        'similarity': matched / len(ref_headings) if ref_headings else 0.0
    }

def compare_keywords(ref_text, student_text, keywords):
    results = []
    
    for keyword in keywords:
        ref_count = len(re.findall(re.escape(keyword), ref_text, re.IGNORECASE))
        student_count = len(re.findall(re.escape(keyword), student_text, re.IGNORECASE))
        
        results.append({
            'keyword': keyword,
            'ref_count': ref_count,
            'student_count': student_count,
            'matched': student_count >= ref_count if ref_count > 0 else True
        })
    
    matched_count = sum(1 for r in results if r['matched'])
    return {
        'details': results,
        'matched_count': matched_count,
        'total_keywords': len(keywords),
        'accuracy': matched_count / len(keywords) if keywords else 0.0
    }

def compare_text_content(ref_text, student_text):
    ref_words = [w.lower() for w in re.findall(r'\w+', ref_text)]
    student_words = [w.lower() for w in re.findall(r'\w+', student_text)]
    
    ref_counter = Counter(ref_words)
    student_counter = Counter(student_words)
    
    common_words = sum(min(ref_counter[w], student_counter[w]) for w in ref_counter)
    total_ref_words = sum(ref_counter.values())
    
    return {
        'common_words': common_words,
        'total_ref_words': total_ref_words,
        'similarity': common_words / total_ref_words if total_ref_words > 0 else 0.0
    }

def compare_images(ref_images_count, student_images_count):
    return {
        'ref_count': ref_images_count,
        'student_count': student_images_count,
        'match': ref_images_count == student_images_count,
        'ratio': student_images_count / ref_images_count if ref_images_count > 0 else 0.0
    }

def detect_reflection(student_text):
    reflection_keywords = [
        '总结', '反思', '体会', '收获', '不足', '改进',
        '经验', '教训', '问题', '建议', '展望', '未来'
    ]
    
    found_keywords = []
    for keyword in reflection_keywords:
        if keyword in student_text:
            found_keywords.append(keyword)
    
    return {
        'has_reflection': len(found_keywords) >= 2,
        'found_keywords': found_keywords,
        'score': min(len(found_keywords) / len(reflection_keywords), 1.0)
    }

def check_format(student_text):
    lines = student_text.split('\n')
    line_lengths = [len(line) for line in lines if line.strip()]
    
    if not line_lengths:
        return {'proper_format': False, 'avg_line_length': 0, 'variance': 0}
    
    avg_length = sum(line_lengths) / len(line_lengths)
    variance = sum((l - avg_length) ** 2 for l in line_lengths) / len(line_lengths)
    
    return {
        'proper_format': avg_length > 20 and variance < 5000,
        'avg_line_length': avg_length,
        'variance': variance
    }