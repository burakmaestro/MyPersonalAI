def calculate_expression(expression):
    """Temel matematik işlemlerini güvenli şekilde hesaplar."""
    try:
        # Güvenlik: sadece belirli karakterlere izin ver
        allowed_chars = "0123456789.+-*/() "
        for ch in expression:
            if ch not in allowed_chars:
                return "Geçersiz karakter bulundu. Sadece sayılar ve +, -, *, /, () kullanılabilir."
        
        # Boşsa uyar
        if not expression.strip():
            return "Lütfen bir matematiksel ifade girin."
        
        # Hesapla
        result = eval(expression)
        return f"Sonuç: {result}"
    
    except ZeroDivisionError:
        return "Sıfıra bölme hatası!"
    except Exception as e:
        return f"Hesaplama hatası: {e}"
