import os
import sys

sys.path.append(r"c:\Users\Himani\Desktop\sih2026")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from predict_complaint import predict_complaint

hybrid_test_queries = [
    # 1. River Heavy Metal (JJM + IIT Dhanbad)
    "River water heavy metal pollution requiring JJM pipe action and IIT Dhanbad filtration.",
    "नदी के पानी में भारी धातुओं का प्रदूषण, जेजेएम पाइप कार्रवाई और आईआईटी धनबाद निस्पंदन (फ़िल्टर) प्रणाली।",
    "River water me heavy metal pollution h JJM pipe action aur IIT Dhanbad filtration chahiye.",
    "rivr watr hevy metl polusion JJM pipe IIT Dhanbad filtrasion",
    
    # 2. Mining Dust (PCB + IIT Dhanbad)
    "Mining dust air pollution requiring pollution control board action and IIT Dhanbad sensor array.",
    "खनन धूल वायु प्रदूषण, प्रदूषण नियंत्रण बोर्ड कार्रवाई और आईआईटी धनबाद सेंसर एर्रे।",
    "Mining dust air pollution ke liye pollution control board action aur IIT Dhanbad sensor array lagao.",
    "minig dust air polution polution control bord IIT Dhanbad sensr",
    
    # 3. Forest Road (PWD + BIT Mesra)
    "Remote forest village connectivity requiring road PWD work and BIT Mesra GIS mapping.",
    "सुदूर वन गांव संपर्क, पीडब्ल्यूडी सड़क निर्माण और बीआईटी मेसरा जीआईएस मैपिंग।",
    "Remote forest village connectivity ke liye road PWD work aur BIT Mesra GIS mapping setup.",
    "remote forst vilage conectivity road PWD work BIT Mesra GIS maping",
    
    # 4. Cattle Epidemic (Vet + BAU Ranchi)
    "Cattle epidemic disease outbreak requiring vet department and BAU Ranchi vaccine logistics.",
    "मवेशी महामारी बीमारी का प्रकोप, पशुपालन विभाग और बीएयू रांची वैक्सीन लॉजिस्टिक्स।",
    "Cattle epidemic disease outbreak rokne ko vet department aur BAU Ranchi vaccine logistics chahiye.",
    "catle epdemik decese outbrk vet departmnt BAU Ranchi vcin logistks",
    
    # 5. Drought Crop Loss (Relief Fund + BAU)
    "Drought crop loss requiring relief fund and BAU drought resistant seed strain.",
    "सूखा फसल क्षति, राहत कोष और बीएयू सूखा प्रतिरोधी बीज किस्म।",
    "Drought crop loss relief fund aur BAU drought resistant seed strain ka issue.",
    "drougt crop los relef fund BAU drougt resstant seed strn",
    
    # 6. Urban Waterlogging (Municipal + BIT Mesra)
    "Urban monsoon waterlogging requiring municipal drain clearing and BIT Mesra hydrodynamic simulation.",
    "शहरी मानसून जलजमाव, नगर निगम नाला सफाई और बीआईटी मेसरा हाइड्रोडायनामिक सिमुलेशन।",
    "Urban monsoon waterlogging me municipal drain clearing aur BIT Mesra hydrodynamic simulation karo.",
    "urbn monsoonn watrloging munispal drain clering BIT Mesra hidrodimik",
    
    # 7. School Roof & Solar (DEO + NIT)
    "School roof leakage and solar power failure requiring district edu action and NIT Microgrid repair.",
    "स्कूल की छत से रिसाव और सौर ऊर्जा विफलता, जिला शिक्षा विभाग कार्रवाई और एनआईटी माइक्रोग्रिड मरम्मत।",
    "School roof leakage aur solar power failure me district edu action aur NIT Microgrid repair request.",
    "skol ruf lekag solr powr falur distrct edu actn NIT Microgrd repr",
    
    # 8. Handpump Fluoride (PHED + CSIR)
    "Handpump fluoride contamination requiring PHE department and CSIR filtration unit.",
    "हैंडपंप फ्लोराइड संदूषण, पीएचई विभाग और सीएसआईआर निस्पंदन इकाई।",
    "Handpump fluoride contamination me PHE department aur CSIR filtration unit ki zaroorat h.",
    "handpmp florid contamnasion PHE departmnt CSIR filtrsn unit",
    
    # 9. Traffic Congestion Blackspot (Police + BIT Mesra)
    "Traffic congestion blackspot requiring police control and BIT Mesra vision signal AI.",
    "यातायात भीड़ भाड़ वाला ब्लैकस्पॉट, पुलिस नियंत्रण और बीआईटी मेसरा विजन सिग्नल एआई।",
    "Traffic congestion blackspot pe police control aur BIT Mesra vision signal AI lagao.",
    "trafic congesion blkspot polse contrl BIT Mesra visn signl AI",
    
    # 10. Tribal Malnutrition (Anganwadi + BAU)
    "Tribal malnutrition requiring Anganwadi ration supply and BAU fortified food RND.",
    "जनजातीय कुपोषण, आंगनवाड़ी राशन आपूर्ति और बीएयू फोर्टिफाइड खाद्य अनुसंधान।",
    "Tribal malnutrition me Anganwadi ration supply aur BAU fortified food RND required.",
    "tribl malnutrisn Anganwdi rasn suply BAU fortfid fod RND"
]

print("================ HYBRID ROUTE VERIFICATION TEST ================\n")
all_passed = True
for idx, q in enumerate(hybrid_test_queries, 1):
    res = predict_complaint(q)
    results = res["results"]
    govt_off = res["government_officer"]
    matched_inst = res["matched_institutions"]
    inst_names = [inst["institution_name"] for inst in matched_inst] if matched_inst else []
    
    route = results["route"]
    cat = results["category"]
    dom = results["domain"]
    
    # Hybrid requirement: Route must be 'Hybrid', Govt Officer MUST be present, and University MUST be present
    is_ok = (route == "Hybrid" and govt_off is not None and len(inst_names) > 0)
    if not is_ok:
        all_passed = False
        
    status = "PASS" if is_ok else "FAIL"
    print(f"Test {idx:02d} [{status}]")
    print(f"  Input:        '{q}'")
    print(f"  Route:        {route}")
    print(f"  Domain:       {dom}")
    print(f"  Category:     {cat}")
    print(f"  Officer:      {govt_off['department_assigned'] if govt_off else 'None'}")
    print(f"  University:   {inst_names}")
    print("-" * 75)

if all_passed:
    print("\nALL 40 HYBRID TEST CASES PASSED PERFECTLY (100% Hybrid Route + Govt Officer + University Allotment)!")
else:
    print("\nSome test cases failed hybrid classification.")
