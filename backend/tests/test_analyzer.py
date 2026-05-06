from app.services.analyzer import analyze_html


def test_analyzer_extracts_core_website_signals():
    html = """
    <html>
      <head>
        <title>Dubai Dental Clinic Appointments</title>
        <meta name="description" content="Book trusted dental treatments in Dubai with experienced dentists and modern care.">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="canonical" href="https://example.com">
      </head>
      <body>
        <nav><a href="/about">About</a><a href="/contact">Contact</a><a href="/services">Services</a></nav>
        <h1>Dental Clinic in Dubai</h1>
        <h2>Book an appointment</h2>
        <a href="/book">Book Appointment</a>
        <form action="/contact"></form>
        <img src="/team.jpg" alt="Dental team">
        <p>Call +971 555 123456 for appointments. Our patients share reviews and testimonials.</p>
      </body>
    </html>
    """
    result = analyze_html("https://example.com", html, response_ms=300, mobile_screenshot=True)
    assert result.website_data["title"] == "Dubai Dental Clinic Appointments"
    assert result.checks["has_h1"] is True
    assert result.scoring["total_score"] > 50

