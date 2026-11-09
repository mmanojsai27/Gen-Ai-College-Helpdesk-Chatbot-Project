
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

documents = {
    "admission_notification.pdf": [
        ("Sample Admission Notification", "Fictional test document"),
        ("Eligibility", "Students must satisfy the eligibility criteria for their selected course."),
        ("Required Documents", "Students should prepare academic certificates, identification proof, recent photographs and entrance examination results where applicable."),
        ("Application Process", "Students should complete the application form and submit the required documents before the stated deadline."),
    ],
    "college_handbook.pdf": [
        ("Sample College Handbook", "Fictional test document"),
        ("Working Hours", "The sample college operates Monday to Saturday from 9:00 AM to 5:00 PM."),
        ("Departments", "The sample departments are CSE, IT, ECE, EEE, Mechanical Engineering and Civil Engineering."),
        ("Hostel", "Hostel availability, room allocation and accommodation charges must be confirmed with the administration."),
    ],
    "fee_structure.pdf": [
        ("Sample Fee Structure", "Fictional test document. These amounts are not actual college fees."),
        ("Tuition Fees", "For testing only, the sample annual tuition fee is Rs. 75,000 for the sample CSE course."),
        ("Scholarships", "Sample scholarships may be available to eligible students subject to institutional rules."),
        ("Fee Concessions", "Students should contact the admissions office to confirm applicable concessions."),
    ],
}

styles = getSampleStyleSheet()

for filename, sections in documents.items():
    file_path = DATA_DIR / filename

    story = []

    for heading, content in sections:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(content, styles["BodyText"]))
        story.append(Spacer(1, 16))

    pdf = SimpleDocTemplate(str(file_path), pagesize=A4)
    pdf.build(story)

    print(f"Created: {file_path}")

print("\nAll sample PDFs created successfully!")
