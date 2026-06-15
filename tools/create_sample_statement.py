from pathlib import Path


OUTPUT_FILE = Path(__file__).resolve().parents[1] / "samples" / "sample_bank_statement.pdf"


LINES = [
    "PINNOSERV DEMO BANK",
    "Sample Bank Statement",
    "",
    "Account holder: Amina Otieno",
    "Account number: 1234567890",
    "Statement period: 01 May 2026 - 31 May 2026",
    "Currency: KES",
    "",
    "Opening balance: 45,000.00",
    "",
    "Date        Description                         Debit       Credit      Balance",
    "2026-05-01  Opening Balance                                  0.00      45,000.00",
    "2026-05-03  Salary Payment                                80,000.00   125,000.00",
    "2026-05-05  Rent Payment                     25,000.00                 100,000.00",
    "2026-05-08  Supermarket Purchase              6,800.00                  93,200.00",
    "2026-05-11  Loan Repayment                   12,000.00                  81,200.00",
    "2026-05-15  Mobile Money Transfer             5,000.00                  76,200.00",
    "2026-05-20  Utility Bill                       3,200.00                  73,000.00",
    "2026-05-26  Client Refund                                  10,000.00    83,000.00",
    "2026-05-31  Closing Balance                                             83,000.00",
    "",
    "Summary",
    "Total credits: 90,000.00",
    "Total debits: 52,000.00",
    "Average balance: 87,500.00",
    "Existing monthly debt payments: 12,000.00",
    "Estimated debt-to-income ratio: 15.0%",
    "",
    "This is a fictional sample statement for testing automated loan scoring."
]


def escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf():
    stream_lines = [
        "BT",
        "/F1 11 Tf",
        "50 790 Td",
        "14 TL",
    ]

    for index, line in enumerate(LINES):
        if index:
            stream_lines.append("T*")
        stream_lines.append(f"({escape_pdf_text(line)}) Tj")

    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = [0]

    for number, content in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(content)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )

    return pdf


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_bytes(build_pdf())
    print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
