# 🔍 Sentiment Analysis - Cách nhận biết tin tức Tích cực/Tiêu cực

## 📋 Tóm tắt

**Sentiment Analysis** (Phân tích cảm xúc) là kỹ thuật AI để tự động xác định thái độ/cảm xúc trong văn bản.

Dự án này sử dụng **VADER** (Valence Aware Dictionary and sEntiment Reasoner) từ thư viện NLTK.

---

## 🎯 Cách hoạt động

### 1️⃣ VADER là gì?

VADER là một công cụ phân tích cảm xúc được tối ưu hóa cho:
- ✅ Social media text
- ✅ Tin tức online
- ✅ Lời bình luận ngắn
- ✅ Cryptocurrency news

### 2️⃣ Quy trình phân tích

```
Văn bản đầu vào
    ↓
VADER Lexicon (từ điển xác định cảm xúc)
    ↓
Tính toán điểm số (Compound Score: -1 to +1)
    ↓
Phân loại (Positive/Negative/Neutral)
    ↓
Trả về: Score + Label + Confidence
```

### 3️⃣ Scoring System

| Compound Score | Label | Emoji | Ý nghĩa |
|---|---|---|---|
| ≥ 0.05 | **POSITIVE** | 😊 | Tích cực |
| ≤ -0.05 | **NEGATIVE** | 😞 | Tiêu cực |
| -0.05 ~ 0.05 | **NEUTRAL** | 😐 | Trung lập |

---

## 📊 Ví dụ thực tế

### ✅ Tin Tích cực (Positive)

```
Tiêu đề: "Bitcoin Reaches New All-Time High"
Nội dung: "Bitcoin has surpassed the previous all-time high, reaching new levels 
          of adoption and market interest. Institutions continue buying..."

📈 VADER Score: 0.81 → POSITIVE ✅
```

**Từ khóa tích cực được phát hiện:**
- "New All-Time High" - tốt lành
- "adoption" - tiến bộ
- "interest" - hứng thú
- "continue buying" - mua tích cực

---

### 😞 Tin Tiêu cực (Negative)

```
Tiêu đề: "Bitcoin Price Crashes Following Negative News"
Nội dung: "Bitcoin has crashed dramatically following negative regulatory news. 
          Panic selling dominates trading volumes."

📉 VADER Score: 0.05 → NEGATIVE ❌
```

**Từ khóa tiêu cực được phát hiện:**
- "Crashes" - sụp đổ
- "Negative" - xấu
- "Panic" - hoảng sợ
- "selling" - bán tháo

---

### 😐 Tin Trung lập (Neutral)

```
Tiêu đề: "Market Volatility Increases Amid Bearish Pressure"
Nội dung: "Recent market trends show increased volatility as investors react 
          to macroeconomic factors."

⚪ VADER Score: 0.49 → NEUTRAL ⚪
```

**Phân tích:**
- "Volatility" - trung tính (không tốt, không xấu)
- "Increased" - có thể tốt hoặc xấu
- "Macroeconomic factors" - chuyên nghiệp, trung lập

---

## 🔧 Cài đặt & Sử dụng

### 1. Cài đặt NLTK

```bash
pip install nltk
```

### 2. Sử dụng trong code

```python
from app.services.sentiment_analyzer import analyze_news_sentiment

# Phân tích một bài báo
result = analyze_news_sentiment(
    title="Bitcoin Reaches New All-Time High",
    content="Bitcoin has surpassed...",
    summary="Bitcoin breaks records"
)

print(result)
# Output:
# {
#     'score': 0.81,           # 0-1 scale
#     'label': 'positive',     # positive/negative/neutral
#     'compound': 0.612,       # VADER raw score (-1 to 1)
#     'confidence': 0.188
# }
```

### 3. Phân tích hàng loạt

```python
from app.services.sentiment_analyzer import batch_analyze_sentiment

news_items = [
    {"title": "...", "content": "...", "summary": "..."},
    {"title": "...", "content": "...", "summary": "..."},
]

# Tự động thêm sentiment_score và sentiment_label
results = batch_analyze_sentiment(news_items)
```

---

## 📈 Kết quả test thực tế

```
Total News Items: 6
  ✅ Positive: 4 (66.7%)
  ❌ Negative: 1 (16.7%)
  ⚪ Neutral: 1 (16.7%)

📊 Average Sentiment Score: 0.63/1.0
```

**Giải thích:**
- 66.7% tin tức tích cực → Thị trường lạc quan
- 16.7% tin tức tiêu cực → Có lo ngại
- 16.7% tin tức trung lập → Sự kiện khách quan

---

## 🎨 Hiển thị UI

Giao diện sẽ hiển thị badges:

```html
<!-- Tích cực -->
<span class="sentiment-badge sentiment-positive">TÍCH CỰC</span>

<!-- Tiêu cực -->
<span class="sentiment-badge sentiment-negative">TIÊU CỰC</span>

<!-- Trung lập -->
<span class="sentiment-badge sentiment-neutral">TRUNG LẬP</span>
```

---

## ⚙️ Cách VADER tính toán

### Bước 1: Tokenize văn bản
```
"Bitcoin Reaches New All-Time High"
↓
["Bitcoin", "Reaches", "New", "All-Time", "High"]
```

### Bước 2: Tra từ điển
```
"Reaches" → neutral (0.0)
"New" → positive (0.1)
"High" → positive (0.2)
↓
Tổng = Positive
```

### Bước 3: Tính Compound Score
```
VADER formula: compound = Σ(sentiment scores) / √(Σ|scores|²)
Range: -1.0 (very negative) to +1.0 (very positive)

Result: 0.612 → POSITIVE
```

---

## 🔬 So sánh các phương pháp

| Method | Ưu điểm | Nhược điểm | Chi phí |
|---|---|---|---|
| **VADER** (hiện tại) | Nhanh, miễn phí, tối ưu news | Không hiểu ngữ cảnh sâu | $0 |
| TextBlob | Đơn giản, miễn phí | Độ chính xác thấp | $0 |
| OpenAI API | Rất chính xác, hiểu ngữ cảnh | Chậm, tốn chi phí | $0.01-0.05/call |
| AWS Comprehend | Chuyên nghiệp, đa ngôn ngữ | Phức tạp, đắt tiền | $0.0001-0.0002/call |

---

## 🚀 Cải thiện trong tương lai

### 1. Fine-tune cho Crypto
```python
# Thêm crypto-specific words vào VADER lexicon
custom_lexicon = {
    'bullish': 0.8,      # Tích cực
    'bearish': -0.8,     # Tiêu cực
    'hodl': 0.5,         # Tích cực
    'dump': -0.6,        # Tiêu cực
    'pump': 0.7,         # Tích cực
}
```

### 2. Kết hợp với AI models
```python
# Sử dụng OpenAI nếu cần độ chính xác cao
if need_high_accuracy:
    result = openai.analyze_sentiment(text)
else:
    result = vader_analyzer.analyze(text)
```

### 3. Multi-language support
```python
# Hỗ trợ nhiều ngôn ngữ
from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="xlm-roberta-base")
```

---

## 📚 Tài liệu

- [VADER: A Parsimonious Rule-based Model](https://github.com/cjhutto/vaderSentiment)
- [NLTK Sentiment Analysis](https://www.nltk.org/api/nltk.sentiment.html)
- [Crypto Sentiment Lexicon](https://github.com/cryptonote/sentiment)

---

## ❓ FAQ

**Q: Tại sao tin "Crypto Markets Face Downturn" lại là POSITIVE?**
A: Vì từ "Face" có thể được hiểu là tiếp cận (positive). Đây là giới hạn của VADER. Với AI models, sẽ chính xác hơn.

**Q: Độ chính xác của VADER là bao nhiêu?**
A: ~80-85% cho tiếng Anh. Tốt cho tin tức, kém hơn cho sarcasm hoặc ngôn ngữ phức tạp.

**Q: Có cách nào để cải thiện độ chính xác?**
A: Có! Thêm crypto-specific lexicon hoặc sử dụng transformer models (BERT, etc.)

---

## 🎓 Học thêm

Xem file test: [test_sentiment.py](../test_sentiment.py)

Chạy test:
```bash
python test_sentiment.py
```

Kết quả sẽ hiển thị chi tiết cách VADER phân tích từng bài báo.
