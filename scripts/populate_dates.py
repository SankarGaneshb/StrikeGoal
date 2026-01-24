
import json

data_path = 'data/exam_dates.json'

updates = {
    "Common Law Admission Test (CLAT) UG": {"start": "July 2025", "end": "October 2025"},
    "NATA": {"start": "February 2026", "end": "May 2026"},
    "National Council for Hotel Management Joint Entrance Examination (NCHM JEE)": {"start": "February 2026", "end": "April 2026"},
    "Bachelor of Design (B.Des.) / NIFT Entrance": {"start": "October 2025", "end": "January 2026"},
    "NEST": {"start": "February 2026", "end": "April 2026"},
    "ISI Admission Test": {"start": "March 2026", "end": "April 2026"},
    "UGEE": {"start": "February 2026", "end": "March 2026"},
    "COMEDK UGET": {"start": "February 2026", "end": "April 2026"},
    "VITEEE": {"start": "November 2025", "end": "March 2026"},
    "SRMJEEE": {"start": "November 2025", "end": "March 2026"},
    "MET (formerly MU-OET)": {"start": "October 2025", "end": "March 2026"},
    "IAT (IISER)": {"start": "April 2026", "end": "May 2026"},
    "UCEED": {"start": "October 2025", "end": "November 2025"},
    "NID-DAT": {"start": "September 2025", "end": "November 2025"},
    "All India Law Entrance Test (AILET)": {"start": "August 2025", "end": "November 2025"},
    "Bachelor of Fashion Technology (B.F.Tech.)": {"start": "October 2025", "end": "January 2026"},
    "NIFT Lateral Entry Admission (NLEA)": {"start": "October 2025", "end": "December 2025"},
    "FDDI AIST": {"start": "February 2026", "end": "April 2026"},
    "AP EAMCET (EAPCET)": {"start": "March 2026", "end": "April 2026"},
    "GPAT": {"start": "January 2026", "end": "February 2026"},
    "CSEET (Company Secretary Executive Entrance Test)": {"start": "October 2025", "end": "December 2025"},
    "AME CET": {"start": "September 2025", "end": "March 2026"}
}

try:
    with open(data_path, 'r') as f:
        data = json.load(f)

    count = 0
    for exam in data['exams']:
        name = exam.get('exam_name')
        if name in updates:
            # Only update if currently null to avoid overwriting existing good data (though in this case we know they are null)
            if exam.get('registration_start') is None:
                exam['registration_start'] = updates[name]['start']
                exam['registration_end'] = updates[name]['end']
                count += 1
                if exam.get('exam_date') == "Not in source":
                     exam['exam_date'] = "Tentative 2026"

    with open(data_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Successfully updated {count} exams with registration dates.")

except Exception as e:
    print(f"Error: {e}")
