"""Model provider abstractions and mock implementation."""
from typing import Protocol, Optional
import time
import re


class ModelProvider(Protocol):
    """Abstract interface for LLM execution."""

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response given a model tag and prompt."""
        ...


def _clean_prompt_text(prompt: str) -> str:
    """Extract raw patient statement from formatted prompt wrappers."""
    # Check for Patient Cebuano Complaint:\n"..."
    m = re.search(r'Patient Cebuano Complaint:\s*["\']?(.*?)["\']?\s*(?:English Clinical Translation:|$)', prompt, re.DOTALL | re.IGNORECASE)
    if m and m.group(1).strip():
        return m.group(1).strip()
    
    # Check for Patient Symptoms (English):\n"..."
    m2 = re.search(r'Patient Symptoms \(English\):\s*["\']?(.*?)["\']?\s*(?:Clinical Guidance:|$)', prompt, re.DOTALL | re.IGNORECASE)
    if m2 and m2.group(1).strip():
        return m2.group(1).strip()

    # Check for English Medical Guidance:\n"..."
    m3 = re.search(r'English Medical Guidance:\s*["\']?(.*?)["\']?\s*(?:Cebuano Medical Guidance:|$)', prompt, re.DOTALL | re.IGNORECASE)
    if m3 and m3.group(1).strip():
        return m3.group(1).strip()

    return prompt.strip()


class MockModelProvider:
    """Deterministic mock provider for stage evaluation and offline development."""

    def __init__(self, simulated_latency_s: float = 0.01) -> None:
        self.simulated_latency_s = simulated_latency_s
        self.call_history = []

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.simulated_latency_s > 0:
            time.sleep(self.simulated_latency_s)

        self.call_history.append({"model": model, "prompt": prompt, "system_prompt": system_prompt})
        clean_text = _clean_prompt_text(prompt)
        lower_prompt = prompt.lower()
        clean_lower = clean_text.lower()
        sys_lower = (system_prompt or "").lower()

        # =====================================================================
        # Stage 1: Cebuano to English translation (Gemma 4)
        # =====================================================================
        if "clinical english" in sys_lower:
            # 1. Pasmo / Kabuhi / Fasting / Night-shift
            if any(w in clean_lower for w in ["pasmo", "kabuhi", "kuto-kuto", "laktaw"]):
                return (
                    "The patient is experiencing tremors, cold sweats, and hyperactive epigastric fluttering ('kabuhi') "
                    "attributed to prolonged fasting, delayed meals ('pasmo'), and excessive caffeine consumption."
                )
            # 2. Panuhot / Cold draft / Thoracic myofascial stiffness
            elif any(w in clean_lower for w in ["panuhot", "nanikig", "gusok", "lusay-lusay", "bukol-bukol"]):
                return (
                    "The patient is experiencing bodily aches, thoracic muscle spasms, and stiffness "
                    "attributed culturally to sudden cold exposure and perspiration drying on the body ('panuhot')."
                )
            # 3. Kalibanga / Diarrhea / Pungko-pungko foodborne
            elif any(w in clean_lower for w in ["kalibanga", "lupot", "pamalaybalay", "pungko", "watery stool", "watery"]):
                return (
                    "The patient suffers from sharp abdominal cramps, hyperactive peristalsis ('pamalaybalay'), "
                    "and frequent watery diarrhea following street food consumption, with risk of hypovolemic dehydration."
                )
            # 4. Pneumonia / Severe respiratory infection (Rust sputum, 39.2C, pleuritic pain)
            elif any(w in clean_lower for w in ["tayaon", "39.2", "plema", "kutsilyo", "dughan"]):
                return (
                    "The patient presents with an unremitting high fever of 39.2°C, persistent productive cough with "
                    "rust-colored sputum ('tayaon'), and sharp pleuritic chest pain concerning for community-acquired pneumonia."
                )
            # 5. Tension headache / Study strain / Screen
            elif any(w in clean_lower for w in ["bakos", "screen", "laptop", "library", "biogesic", "piyong"]):
                return (
                    "The patient presents with severe circumferential band-like tension headache ('bakos sa agtang') "
                    "and digital asthenopia (eye strain) exacerbated by prolonged laptop screen exposure."
                )
            # 6. Motion sickness / Dizziness during vehicular travel
            elif any(w in clean_lower for w in ["car", "ride", "sakyanan", "byahi", "biyahe", "bapor", "kinetosis"]) or ("malipong" in clean_lower and "car" in clean_lower):
                return (
                    "The patient experiences episodic motion sickness (kinetosis) and vestibular dizziness "
                    "during vehicular travel, with associated lightheadedness and mild nausea."
                )
            # 7. Generalized headache / Ulo
            elif any(w in clean_lower for w in ["ulo", "headache", "labad", "agtang"]):
                return "The patient presents with a severe throbbing headache requiring clinical evaluation."
            # 8. Generalized fever / ubo
            elif any(w in clean_lower for w in ["hilanat", "ubo"]):
                return "The patient presents with an elevated fever and productive cough."
            # 9. Pamaol / Muscle soreness
            elif any(w in clean_lower for w in ["pamaol", "kapoy", "kaunoran"]):
                return "The patient reports diffuse musculoskeletal aches and soreness following strenuous physical exertion ('pamaol')."
            elif "sakit" in clean_lower and "tiyan" in clean_lower:
                return "The patient suffers from sharp abdominal cramps and frequent watery diarrhea."

            # Clean fallback for any other custom input
            return f"The patient reports the following clinical complaint: {clean_text}"

        # =====================================================================
        # Stage 2: MedGemma Medical Consultation (English)
        # =====================================================================
        if "medgemma" in model.lower() or "clinical ai" in sys_lower or "medical guidance" in sys_lower:
            # Motion sickness (must use full phrases so 'car' doesn't match 'care')
            if any(w in lower_prompt for w in ["motion sickness", "kinetosis", "vehicular travel", "vestibular dizziness", "vestibular disturbance"]):
                return (
                    "Clinical Assessment: The symptoms are consistent with motion sickness (kinetosis) and vestibular disturbance "
                    "provoked by vehicular motion.\n\n"
                    "Supportive Care: Sit in the front passenger seat facing the direction of travel and fix your gaze on the distant horizon; "
                    "ensure adequate cool ventilation and avoid reading screens or books while moving; take small sips of water or ginger tea. "
                    "Over-the-counter dimenhydrinate or meclizine may be taken 30-60 minutes before travel if approved by a pharmacist.\n\n"
                    "Red Flags: Urgent medical evaluation is necessary if dizziness persists when stationary, or is accompanied by sudden hearing loss, "
                    "focal neurological signs (slurred speech, limb weakness), or syncope."
                )
            # Tension headache
            elif any(w in lower_prompt for w in ["headache", "tension", "screen", "asthenopia", "agtang", "eye strain"]):
                return (
                    "Clinical Assessment: The presentation is typical of a tension-type headache compounded by digital eye strain (asthenopia) "
                    "from prolonged screen study.\n\n"
                    "Supportive Care: Implement the 20-20-20 rule (every 20 minutes, look at an object 20 feet away for 20 seconds); dim laptop brightness; "
                    "rest in a quiet, dark environment; maintain hydration (at least 2 liters of water daily); and apply a cool cloth to the forehead. "
                    "Paracetamol may be used for symptomatic relief per label instructions.\n\n"
                    "Red Flags: Seek emergency care if the headache is sudden and 'thunderclap' in severity, or accompanied by neck stiffness, high fever, "
                    "photophobia, or visual field deficits."
                )
            # Panuhot / Myofascial spasm
            elif any(w in lower_prompt for w in ["panuhot", "myofascial", "thoracic", "stiffness", "spasm", "cold exposure"]):
                return (
                    "Clinical Assessment: Consistent with acute myofascial pain syndrome and thoracic muscle spasms triggered by cold draft exposure "
                    "and rapid evaporative cooling ('panuhot').\n\n"
                    "Supportive Care: Apply warm compresses or take a warm shower to relax hypertonic muscles; perform gentle cervical and shoulder range-of-motion "
                    "stretches; avoid sitting directly in front of cold air fans; and stay hydrated. Light, gentle topical rub with soothing oils is acceptable, "
                    "but avoid forceful or aggressive deep tissue kneading on inflamed points.\n\n"
                    "Red Flags: Seek immediate clinical evaluation if pain radiates down the left arm, is accompanied by chest tightness, diaphoresis, "
                    "shortness of breath, or numbness in the upper extremities."
                )
            # Pasmo / Kabuhi / Fasting hypoglycemia
            elif any(w in lower_prompt for w in ["pasmo", "kabuhi", "tremors", "fasting", "hypoglycemia", "gastritis", "caffeine"]):
                return (
                    "Clinical Assessment: Features suggest acute fasting hypoglycemia combined with hyperacidic dyspepsia ('kabuhi') and sympathetic "
                    "activation from prolonged fasting and excessive caffeine intake ('pasmo').\n\n"
                    "Supportive Care: Consume a balanced complex carbohydrate and protein snack immediately (e.g., rice, warm soup, oatmeal); discontinue energy "
                    "drinks and empty-stomach black coffee; transition to regular, small, frequent meals throughout work shifts; and drink adequate water.\n\n"
                    "Red Flags: Emergency medical care is required if the patient experiences fainting (syncope), confusion, persistent vomiting, or signs "
                    "of gastrointestinal bleeding such as black tarry stools."
                )
            # Pneumonia / Chest / Rust Sputum
            elif any(w in lower_prompt for w in ["pneumonia", "consolidation", "tayaon", "sputum", "pleuritic", "39.2"]):
                return (
                    "Clinical Assessment: The clinical picture is strongly indicative of community-acquired pneumonia (CAP) with pleurisy and potential "
                    "pulmonary consolidation - a serious lower respiratory infection.\n\n"
                    "Antimicrobial Stewardship & Referral: Strictly DO NOT self-medicate with leftover or borrowed antibiotics. The patient urgently requires "
                    "formal in-person medical evaluation, chest radiography (X-ray), and targeted prescription therapy under a physician's care.\n\n"
                    "Supportive Care: Rest in an upright or semi-Fowler position to facilitate lung expansion; stay well hydrated with warm fluids; monitor body temperature.\n\n"
                    "Red Flags: PROCEED IMMEDIATELY TO THE EMERGENCY ROOM if experiencing shortness of breath at rest, rapid respiratory rate, cyanosis (bluish lips or nails), "
                    "or mental confusion."
                )
            # Diarrhea / Gastroenteritis
            elif any(w in lower_prompt for w in ["diarrhea", "gastroenteritis", "pamalaybalay", "kalibanga", "cramps", "dehydration", "ciprofloxacin"]):
                return (
                    "Clinical Assessment: Acute watery gastroenteritis with cramping, likely from contaminated food/water, carrying high risk of dehydration.\n\n"
                    "Antimicrobial Stewardship: Strictly DO NOT initiate self-administered ciprofloxacin or any unprescribed antibiotics; routine watery diarrhea does not "
                    "warrant empiric antibiotics and risks severe antimicrobial resistance.\n\n"
                    "Supportive Care: Immediately prioritize Oral Rehydration Salts (ORS) - dissolve 1 sachet in 1 liter of safe water and drink 1 glass after each loose stool; "
                    "follow a bland diet (rice congee, bananas, crackers); avoid dairy and greasy foods.\n\n"
                    "Red Flags: Seek immediate hospital emergency care if experiencing sunken eyes, extreme lethargy, inability to urinate (anuria), persistent vomiting, "
                    "or visible blood in stool."
                )

            # Default fallback for other conditions
            return (
                "Clinical Assessment: The reported symptoms require preliminary evaluation to determine underlying etiology and severity.\n\n"
                "Supportive Care: Maintain adequate oral hydration with clean fluids, rest in a comfortable environment, avoid strenuous physical exertion, "
                "and refrain from self-administering unprescribed medications or antibiotics.\n\n"
                "Red Flags: Consult a licensed physician or visit the nearest health facility immediately if symptoms worsen, or if you develop high persistent fever, "
                "shortness of breath, severe pain, or extreme weakness."
            )

        # =====================================================================
        # Stage 3: English to Cebuano translation (Gemma 4)
        # =====================================================================
        if ("cebuano" in sys_lower or "bisaya" in sys_lower) and ("translate" in sys_lower or "communicator" in sys_lower):
            # Motion sickness
            if any(w in lower_prompt for w in ["motion sickness", "kinetosis", "vehicular motion", "dimenhydrinate", "meclizine"]):
                return (
                    "Base sa imong gipamati, kini nagtimaan sa 'motion sickness' (pagkalipong ug kasukaon tungod sa biyahe sa sakyanan o sakayan).\n\n"
                    "Tambag sa Pag-atiman: Lingkod sa atubangan nga bahin sa sakyanan nga nagtan-aw sa layong unahan; ablihi ang bintana aron makasulod ang preskong "
                    "hangin; ug ayaw pagtan-aw sa cellphone o pagbasa samtang nagdagan ang sakyanan. Mahimo kang moinom og hinay-hinay nga tubig o tsa nga luy-a. "
                    "Kon gikinahanglan, pwede mangutana sa botika bahin sa tambal sa biyahe (sama sa meclizine) 30 minutos sa dili pa mobiyahe.\n\n"
                    "Pahimangno: Pakigkita dayon sa doktor kon ang pagkalipong magpadayon bisan wala na magbiyahe, o kon dunay pamikog sa lawas o pagkahanaw sa panimbang."
                )
            # Tension headache
            elif any(w in lower_prompt for w in ["headache", "tension", "screen", "asthenopia", "agtang", "eye strain"]):
                return (
                    "Base sa imong mga simtomas, kini nagpakita og tension headache (labad sa ulo tungod sa tensiyon ug kahago) nga gisagolan og pagkapoy sa "
                    "mga mata (eye strain) gumikan sa dugay nga pagtan-aw sa laptop screen samtang nagtuon.\n\n"
                    "Tambag sa Pag-atiman: Ipatuman ang lagda nga 20-20-20 (matag 20 minutos nga pagtan-aw sa screen, ipiyong o itan-aw ang mata sa layo sulod sa "
                    "20 segundos); pahuway sa mangitngit ug hilom nga kwarto; pag-inom og daghang tubig; ug pwede mogamit og bugnawng panapton sa agtang. "
                    "Ang paracetamol makatabang pagsanta sa kasakit sumala sa saktong giya sa pakete.\n\n"
                    "Pahimangno: Pakigkita dayon sa doktor kon ang labad sa ulo kalit kaayong mograbe sama sa kilat, kon gahi ang liog, dunay taas nga hilanat, "
                    "o kon malubog ang panan-aw."
                )
            # Panuhot / Myofascial spasm
            elif any(w in lower_prompt for w in ["panuhot", "myofascial", "thoracic", "stiffness", "spasm", "cold exposure"]):
                return (
                    "Base sa imong gibati, kini nagpakita og 'panuhot' kun acute myofascial muscle spasm (panikig sa kaunoran sa abaga ug likod) tungod sa "
                    "kabugnaw sa hangin, ulan, o pagkahupas sa singot sa lawas.\n\n"
                    "Tambag sa Pag-atiman: Butangi og mainit-init nga compress (panapton o botelya nga may init tubig) ang abaga ug likod aron magrelaks ang "
                    "kaunoran; paghimo og hinay nga pag-inat-inat; pagsul-ob og komportableng sinina nga dili mabugnawan; ug pahuway og tarung. Ang hinay nga paghaplas "
                    "og lana nga may luy-a makatabang, apan likayi ang kusog kaayong pagpislit o paghilot kon magsakit pa.\n\n"
                    "Pahimangno: Magpakonsulta gilayon kon ang kasakit molahos sa dughan, maglisod sa pagginhawa, o kon mobati og pamikog ug pagkamanhid sa mga bukton."
                )
            # Pasmo / Kabuhi
            elif any(w in lower_prompt for w in ["pasmo", "kabuhi", "tremors", "fasting", "hypoglycemia", "gastritis", "caffeine"]):
                return (
                    "Base sa imong gipamati, kini nagtimaan sa 'pasmo' ug 'kabuhi' (hypoglycemia ug pagsulbong sa asido sa tiyan) tungod sa paglaktaw-laktaw sa tingkaon, "
                    "dugay nga pagpuasa samtang nag-night shift, ug paghinobra sa pag-inom og kape ug energy drinks.\n\n"
                    "Tambag sa Pag-atiman: Kaon dayon og masustansyang pagkaon sama sa kan-on, sabaw, o biskwit; undang una sa kape ug energy drinks; pagkaon sa "
                    "saktong oras bisan ginagmay apan kanunay (small frequent meals); ug inom og igo nga tubig.\n\n"
                    "Pahimangno: Adto dayon sa ospital o klinika kon malipong hangtod makuyapan, magsigeg suka nga dili na mahunong, o kon itom ang hugaw nga murag alkitran."
                )
            # Pneumonia
            elif any(w in lower_prompt for w in ["pneumonia", "consolidation", "tayaon", "sputum", "pleuritic", "39.2"]):
                return (
                    "Base sa imong mga gipamati, kini nagtimaan sa posibleng grabe nga impeksyon sa baga kun pulmonya (pneumonia) nga may 'pleurisy' (kasakit sa kilid sa dughan "
                    "tungod sa panghubag), ilabina kay dunay tayaon nga plema ug taas kaayong hilanat nga 39.2°C sulod na sa duha ka semana.\n\n"
                    "Hugot nga Pahimangno sa Tambal: AYAW pag-inom og bisan unsang subra o hinuwaman nga antibiotic gikan sa silingan; kinahanglan ka og dinalian nga "
                    "eksaminasyon sa doktor ug Chest X-ray aron masuta ang tinuod nga kahimtang sa baga ug mahatagan sa eksaktong resita.\n\n"
                    "Tambag sa Pag-atiman: Pahuway nga medyo nag-alirong o sinandig ang lawas aron mas luag ang pagginhawa, pag-inom og igo nga tubig, ug monitora ang temperatura.\n\n"
                    "Dinalian nga Pasidaan: ADTO GILAYON SA EMERGENCY ROOM kon maglisod na sa pagginhawa, kon paspas kaayo ang paghupoy-hupoy sa dughan, kon maglagom ang ngabil "
                    "o kuko, o kon maglibog na ang huna-huna."
                )
            # Diarrhea / Kalibanga
            elif any(w in lower_prompt for w in ["diarrhea", "gastroenteritis", "pamalaybalay", "kalibanga", "cramps", "dehydration", "ciprofloxacin"]):
                return (
                    "Base sa imong mga simtomas, kini nagpakita og acute gastroenteritis (kalibanga o impeksyon sa tiyan) gikan sa kontaminadong pagkaon, nga dunay peligro sa "
                    "pagka-dehydrate o pagkahubas sa tubig sa lawas.\n\n"
                    "Hugot nga Pahimangno sa Tambal: AYAW pag-inom og ciprofloxacin o bisan unsang antibiotics nga walay resita sa doktor; delikado kini, makamugna og resistensya "
                    "sa kagaw, ug makadaot sa lawas.\n\n"
                    "Tambag sa Pag-atiman: Ang labing importante mao ang pag-inom og Oral Rehydration Salts (ORS) nga gitunaw sa 1 ka litro nga limpyo nga tubig - inom og usa ka "
                    "baso matag human og kalibang; kaon og humok ug ordinaryong pagkaon sama sa lugaw, saging, ug crackers; likayi ang mantikaon ug gatas.\n\n"
                    "Pahimangno sa Katalagman: Adto gilayon sa Emergency Room kon dunay dugo sa hugaw, kon dili na makatunon og tubig kay magsige'g suka, kon taas kaayo ang hilanat, "
                    "o kon wala na mangihi ug luya kaayo ang lawas."
                )

            # Default fallback for Cebuano translation
            return (
                "Base sa imong mga gipahibalo bahin sa imong pamati:\n\n"
                "Tambag sa Pag-atiman: Pahuway sa komportable nga dapit, pag-inom og igo nga limpyo nga tubig, bantayi ang dagan sa imong mga simtomas, ug likayi una ang bug-at "
                "nga mga buluhaton. Ayaw pag-inom og mga tambal o antibiotics nga walay resita sa lisensyadong doktor.\n\n"
                "Pahimangno: Pakigkita gilayon sa labing duol nga health center, klinika, o ospital kon magkagrabe ang kasakit, kon dunay taas nga hilanat, maglisod sa pagginhawa, "
                "o kon magluya pag-ayo ang lawas."
            )

        # Default fallback
        return f"[Mock response from {model}]: {clean_text}"
