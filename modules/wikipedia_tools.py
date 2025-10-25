import wikipedia

# Wikipedia dilini Türkçe olarak ayarla
wikipedia.set_lang("tr")

def get_wikipedia_summary(query, sentences=3):
    """Wikipedia'dan kısa bir özet getirir."""
    try:
        results = wikipedia.search(query)
        if not results:
            return f"'{query}' hakkında bir sonuç bulunamadı."

        page = wikipedia.page(results[0])
        summary = wikipedia.summary(page.title, sentences=sentences)
        return f"{page.title} — {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"'{query}' için birden fazla sonuç bulundu: {', '.join(e.options[:3])}..."
    except wikipedia.exceptions.PageError:
        return f"'{query}' adlı bir Wikipedia sayfası bulunamadı."
    except Exception as e:
        return f"Wikipedia sorgusu başarısız: {e}"
