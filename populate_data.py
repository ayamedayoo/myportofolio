import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portofolio.settings")
django.setup()

from main.models import Project, Experience, Award

def populate():
    # Projects
    if Project.objects.count() == 0:
        print("Populating initial Project data from CV...")
        Project.objects.create(
            title="Niskala Blockchain Based Carbon Marketplace",
            description="• Platform Engineering: Engineered the operational dashboards and foundational logic for the multi-sided platform utilizing object-oriented programming.\n• Quality Assurance & Testing: Executed systematic logic verification and unit testing methodologies.\n• Financial Modeling & Strategy: Formulated a comprehensive 5-year business roadmap and financial projections.",
            role="Personal Project",
            started_at=date(2026, 4, 1),
            ended_at=date(2026, 6, 30)
        )
        Project.objects.create(
            title="AINGINEER",
            description="• System Engineering & Web Development: Architected and developed the core infrastructure of the application.\n• Data Science & Analytics: Designed predictive models and data pipelines to extract actionable insights.\n• Business Intelligence: Implemented data visualization dashboards.",
            role="Personal Project",
            started_at=date(2026, 2, 1),
            ended_at=date(2026, 5, 31)
        )
        print("Project data populated successfully.")
    else:
        print("Projects already exist in the database.")

    # Experience
    if Experience.objects.count() == 0:
        print("Populating initial Experience data from CV...")
        experiences = [
            ("President - Majelis Perwakilan Kelas SMAN 9 Bekasi", "• Establish regulations regarding discipline\n• Monitor and review the performance of the Student Council\n• Be accountable to the principal regarding school activities.\n• Report aspirations to the school\n(2022 - 2023)"),
            ("President - Asosiasi MPK se-Bekasi", "• Serve as a communication platform between schools in Bekasi City\n• Lead the volunteer program in Bekasi\n• Serve as a forum for discussion and deliberation regarding the MPK regulatory mechanisms in Bekasi\n(2023 - 2024)"),
            ("Head of Division - Departemen Kesejahteraan Mahasiswa FTSL 24", "• Design and manage student welfare programs.\n• Channel student aspirations and needs to the campus.\n• Oversee the implementation and evaluation of welfare programs.\n(2024)"),
            ("Staff PSDM - TPB CUP 2024", "• Assist with the recruitment and training of team members.\n• Support human resource development during the event.\n• Manage personnel-related administration and documentation.\n(2024)"),
            ("Wakil Mahasiswa ITB - Majelis Wali Amanat", "• Conducting strategic studies on ITB policy drafts\n• Advocating for students to the rectorate\n(2025)"),
            ("Kajian Strategis - Keluarga Mahasiswa ITB", "• Conducting studies on national issues\n• Advocating for student issues with the ITB Student Family Cabinet\n(2025)"),
            ("Founder - Kanal Pendidikan Filsafat Epistemologi", "• Design and manage philosophical educational content related to epistemology.\n• Facilitate discussions and critical studies on theories of knowledge.\n• Coordinate educational activities and channel publications.\n(2025)"),
            ("Aksi Angkatan dan Pengabdian FTSL 24", "• Teaching elementary school students at SDN Jatinangor\n• Disability day with survivors in Jatinangor\n(2025)"),
            ("Aksi Angkatan dan Pengabdian Ardhacandra Vegha", "• Conducting donation collection and teaching at 5 orphanages\n(2025)")
        ]
        
        for title, desc in experiences:
            exp = Experience.objects.create(
                title=title,
                description=desc,
                category='volunteer',
                ended_at=date(2025, 12, 31) # arbitrary end date for non-ongoing
            )
        print("Experience data populated successfully.")
    else:
        print("Experiences already exist in the database.")

    # Awards
    if Award.objects.count() == 0:
        print("Populating initial Award data from CV...")
        awards = [
            ("1st Place in the SCC SRE Reveal Study Case Competition", "Society of Renewable Energy (SRE), Brawijaya University", 2025),
            ("1st Place in the Macroeconomics Essay Competition", "Capital Market Study Group (KSPM), FEB UI", 2022),
            ("1st Place (Group) in the PROIN Digital and Sustainable Business Competition", "Binus University", 2023),
            ("1st Place (Individual) in the Ciputra Tourism Week Digital Business Plan Competition", "Ciputra University", 2022),
            ("3rd Place (Individual) in the UII Envirolympics LKTI Competition", "Islamic University of Indonesia", 2023),
            ("1st Place (Individual) in the INSPIRE NATION Business Plan Competition", "Pakuan University", 2023),
            ("2nd Place (Individual) in the INSPACE Information Systems Scientific Writing Competition", "Kalimantan Institute of Technology", 2022),
            ("1st Place (Individual) in the SPARKLING 2023 Digital Business Plan Competition", "Kak Seto School", 2023),
            ("1st Place (Individual) in the Information Systems Digital Business Plan Competition", "Satya Negara Indonesia University", 2022),
            ("1st Place (Individual) in the National Speech Competition", "Discover.me", 2022),
            ("2nd Place (Individual) in the Kidspreneurship National App and Game Category", "University of Western Australia and Harapan Bangsa School", 2021),
            ("2nd Place (Individual) in the Philosophy Essay, Philosophy Week 2022", "Widya Mandala Catholic University, Surabaya", 2022),
            ("3rd Place (Individual) in the SVP Innovation War Digital Competition", "Bekasi City Government", 2021),
            ("Finalist (Individual) IMPRENEUR Digital Business Plan Competition", "Binus University", 2023),
            ("Finalist (Individual) Envirolympics 2022 Scientific Paper Competition", "Environmental Engineering, Islamic University of Indonesia", 2022),
            ("Individual Finalist in the 2023 FIKSI Competition", "National Achievement Center, Ministry of Education and Culture", 2023),
            ("Individual Finalist in the Ganesha Business Festival Competition", "School of Business and Management, Bandung Institute of Technology", 2023)
        ]

        for title, issuer, year in awards:
            Award.objects.create(
                title=title,
                issuer=issuer,
                year=year
            )
        print("Award data populated successfully.")
    else:
        print("Awards already exist in the database.")

if __name__ == '__main__':
    populate()
