"""Kurzer Verbindungstest: Funktioniert der API-Key aus den GitHub Secrets?

Der Key wird nie im Code gespeichert. Das Anthropic-SDK liest ihn automatisch
aus der Umgebungsvariable ANTHROPIC_API_KEY, die GitHub Actions setzt.
"""
import anthropic

client = anthropic.Anthropic()

antwort = client.messages.create(
    model="claude-haiku-5-5",  # kleinstes, günstigstes Modell reicht für den Test
    max_tokens=50,
    messages=[{"role": "user", "content": "Antworte nur mit: Verbindung steht."}],
)

print("Antwort der API:", antwort.content[0].text)
print("Verbrauchte Tokens (Ein/Aus):", antwort.usage.input_tokens, "/", antwort.usage.output_tokens)
