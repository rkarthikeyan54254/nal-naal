#!/usr/bin/env python3
"""
Tamil Nal panchangam generator — Drik-ganita (Swiss Ephemeris / Lahiri)
with a Pambu Panchangam (Vakyam) override layer.

Run:  python3 generate_panchangam.py
Output: writes data.json in the same folder (full year from Aadi 1).

To correct any date against your physical Pambu Panchangam, edit OVERRIDES below
(or overrides.json if present) and re-run. Overrides always win over computation.
"""
import swisseph as swe, datetime, json, os

swe.set_sid_mode(swe.SIDM_LAHIRI)

NAK_TA = ["அசுவினி","பரணி","கார்த்திகை","ரோகிணி","மிருகசீரிடம்","திருவாதிரை",
"புனர்பூசம்","பூசம்","ஆயில்யம்","மகம்","பூரம்","உத்திரம்","அஸ்தம்","சித்திரை",
"சுவாதி","விசாகம்","அனுஷம்","கேட்டை","மூலம்","பூராடம்","உத்திராடம்","திருவோணம்",
"அவிட்டம்","சதயம்","பூரட்டாதி","உத்திரட்டாதி","ரேவதி"]
NAK_EN = ["Ashwini","Bharani","Krithigai","Rohini","Mrigasheersham","Thiruvathirai",
"Punarpoosam","Poosam","Aayilyam","Magam","Pooram","Uttiram","Astham","Chithirai",
"Swathi","Visakam","Anusham","Kettai","Moolam","Pooradam","Uttiradam","Thiruvonam",
"Avittam","Sadhayam","Poorattathi","Uttirattathi","Revathi"]
TITHI_TA = ["பிரதமை","துவிதியை","திருதியை","சதுர்த்தி","பஞ்சமி","சஷ்டி","சப்தமி",
"அஷ்டமி","நவமி","தசமி","ஏகாதசி","துவாதசி","திரயோதசி","சதுர்த்தசி","பௌர்ணமி",
"பிரதமை","துவிதியை","திருதியை","சதுர்த்தி","பஞ்சமி","சஷ்டி","சப்தமி","அஷ்டமி",
"நவமி","தசமி","ஏகாதசி","துவாதசி","திரயோதசி","சதுர்த்தசி","அமாவாசை"]
TAMIL_MONTHS = ["சித்திரை","வைகாசி","ஆனி","ஆடி","ஆவணி","புரட்டாசி",
                "ஐப்பசி","கார்த்திகை","மார்கழி","தை","மாசி","பங்குனி"]
TAMIL_MONTHS_EN = ["Chithirai","Vaikasi","Aani","Aadi","Avani","Purattasi",
                   "Aippasi","Karthigai","Margazhi","Thai","Masi","Panguni"]
WEEKDAYS_TA = ["திங்கட்கிழமை","செவ்வாய்க்கிழமை","புதன்கிழமை","வியாழக்கிழமை",
               "வெள்ளிக்கிழமை","சனிக்கிழமை","ஞாயிற்றுக்கிழமை"]

FLAG = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
def _jd(y,m,d,h=6.0): return swe.julday(y,m,d, h-5.5)  # IST->UT
def _ms(jd):
    moon = swe.calc_ut(jd, swe.MOON, FLAG)[0][0]
    sun  = swe.calc_ut(jd, swe.SUN, FLAG)[0][0]
    return moon, sun
def nak(y,m,d):
    moon,_ = _ms(_jd(y,m,d)); i = int(moon//(360/27))%27; return i, NAK_TA[i], NAK_EN[i]
def tithi(y,m,d):
    moon,sun = _ms(_jd(y,m,d)); i = int(((moon-sun)%360)//12); return i, TITHI_TA[i]
def sun_rasi(y,m,d):
    sun = swe.calc_ut(_jd(y,m,d), swe.SUN, FLAG)[0][0]; return int(sun//30)
def tamil_md(y,m,d):
    r = sun_rasi(y,m,d); probe = datetime.date(y,m,d); n=1
    while True:
        p = probe - datetime.timedelta(days=1)
        if sun_rasi(p.year,p.month,p.day) != r: break
        probe = p; n += 1
    return TAMIL_MONTHS[r], TAMIL_MONTHS_EN[r], n

# ============ Daily time-bands (Rahukaalam etc.), Gowri, Chandrashtamam ============
CHENNAI_LAT, CHENNAI_LON = 13.0827, 80.2707
_GEO = (CHENNAI_LON, CHENNAI_LAT, 0.0)

def sun_events(y, m, d):
    """(sunrise, sunset) as IST decimal hours at Chennai."""
    jd0 = swe.julday(y, m, d, 0.0)
    r = swe.rise_trans(jd0 - 0.5, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, _GEO)[1][0]
    s = swe.rise_trans(jd0 - 0.5, swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER, _GEO)[1][0]
    to = lambda jd: (swe.revjul(jd)[3] + 5.5) % 24
    return to(r), to(s)

def _hm(h):
    h %= 24
    return f"{int(h):02d}:{int((h % 1) * 60):02d}"

# weekday (python Mon=0..Sun=6) -> which of 8 day-segments the band occupies
_RAHU = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
_YAMA = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
_KULI = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

# Gowri Panchangam day sequence per weekday (8 periods from sunrise)
_GOWRI_DAY = {
 6: ['உதி','அமிர்தம்','ரோகம்','லாபம்','தனம்','சுகம்','காந்தம்','சோரம்'],
 0: ['அமிர்தம்','ரோகம்','லாபம்','தனம்','சுகம்','காந்தம்','சோரம்','உதி'],
 1: ['ரோகம்','லாபம்','தனம்','சுகம்','காந்தம்','சோரம்','உதி','அமிர்தம்'],
 2: ['லாபம்','தனம்','சுகம்','காந்தம்','சோரம்','உதி','அமிர்தம்','ரோகம்'],
 3: ['தனம்','சுகம்','காந்தம்','சோரம்','உதி','அமிர்தம்','ரோகம்','லாபம்'],
 4: ['சுகம்','காந்தம்','சோரம்','உதி','அமிர்தம்','ரோகம்','லாபம்','தனம்'],
 5: ['காந்தம்','சோரம்','உதி','அமிர்தம்','ரோகம்','லாபம்','தனம்','சுகம்'],
}
_GOWRI_GOOD = {'அமிர்தம்','சுகம்','லாபம்','தனம்','உதி'}

_RASIS_TA = ['மேஷம்','ரிஷபம்','மிதுனம்','கடகம்','சிம்மம்','கன்னி',
             'துலாம்','விருச்சிகம்','தனுசு','மகரம்','கும்பம்','மீனம்']

def time_bands(y, m, d):
    sr, ss = sun_events(y, m, d)
    seg = (ss - sr) / 8
    wd = datetime.date(y, m, d).weekday()
    def band(n):
        st = sr + (n - 1) * seg
        return [_hm(st), _hm(st + seg)]
    # Gowri periods (day) + the good "Nalla Neram" windows
    gowri = []
    good = []
    for i, name in enumerate(_GOWRI_DAY[wd]):
        st = sr + i * seg
        g = "good" if name in _GOWRI_GOOD else "bad"
        gowri.append([_hm(st), _hm(st + seg), name, g])
        if g == "good":
            good.append([_hm(st), _hm(st + seg)])
    # Chandrashtamam: 8th rasi from Moon's rasi at ~6am
    moon = swe.calc_ut(swe.julday(y, m, d, 0.5), swe.MOON, FLAG)[0][0]
    chandra = _RASIS_TA[(int(moon // 30) + 7) % 12]
    return {
        "sunrise": _hm(sr), "sunset": _hm(ss),
        "rahu": band(_RAHU[wd]), "yama": band(_YAMA[wd]), "kuligai": band(_KULI[wd]),
        "nallaNeram": good[:3], "gowri": gowri, "chandrashtamam": chandra
    }


PHOTO = {
 "ekadasi":("images/g-vishnu.jpg","Vishnu · Perumal"),
 "pradosham":("images/g-shiva.jpg","Shiva & Nandi"),
 "shivaratri":("images/g-bhairavar.jpg","Bhairava · Shiva"),
 "amman":("images/g-durga.jpg","Durga · Amman"),
 "chevvai":("images/g-durga.jpg","Durga · Amman"),
 "pooram":("images/new-aandaal.jpg","Aandaal"),
 "sashti":("images/g-murugar.jpg","Murugan"),
 "krithigai":("images/g-murugar.jpg","Murugan"),
 "chaturthi":("images/g-ganesh.jpg","Ganesha"),
 "pournami":("images/g-pournami.jpg","பௌர்ணமி · Full Moon"),
 "amavasai":("images/g-amavasai.jpg","அமாவாசை · New Moon"),
 "onam":("images/g-vishnu.jpg","Vishnu · Perumal"),
 "krishna":("images/g-krishna.jpg","Krishna"),
 "rama":("images/g-rama.jpg","Rama"),
 "hanuman":("images/g-hanumar.jpg","Hanuman"),
 "guru":("images/g-saraswathi.jpg","Saraswati"),
}
PRIO = ["krishna","rama","hanuman","pooram","ekadasi","pradosham","shivaratri","sashti","krithigai","chaturthi","pournami","guru","onam","amman","amavasai"]

# Nakshatram -> presiding deity image (authentic Tamil tradition; Anusham -> Periyava per family).
# Every day therefore shows a real deity image based on its star.
NAK_DEITY = {
 "Ashwini":   ("images/g-saraswathi.jpg","சரஸ்வதி","Saraswati — star lord of Ashwini"),
 "Bharani":   ("images/g-abirami.jpg","அபிராமி","Abirami — star lord of Bharani"),
 "Krithigai": ("images/g-murugar.jpg","முருகன்","Murugan — star lord of Krithigai"),
 "Rohini":    ("images/g-krishna.jpg","கிருஷ்ணன்","Krishna — star lord of Rohini"),
 "Mrigasheersham":("images/g-shiva.jpg","சிவன்","Shiva — star lord of Mrigasheersham"),
 "Thiruvathirai":("images/g-shiva.jpg","சிவன்","Shiva — star lord of Thiruvathirai"),
 "Punarpoosam":("images/g-rama.jpg","ராமர்","Rama — star lord of Punarpoosam"),
 "Poosam":    ("images/g-shiva.jpg","தட்சிணாமூர்த்தி","Dakshinamurthy — star lord of Poosam"),
 "Aayilyam":  ("images/new-naga.jpg","ஆதிசேஷன்","Adisesha Naga — star lord of Aayilyam"),
 "Magam":     ("images/new-surya.jpg","சூரிய நாராயணர்","Surya Narayana — star lord of Magam"),
 "Pooram":    ("images/new-aandaal.jpg","ஆண்டாள்","Aandaal — star lord of Pooram"),
 "Uttiram":   ("images/new-lakshmi.jpg","மகாலட்சுமி","Mahalakshmi — star lord of Uttiram"),
 "Astham":    ("images/g-saraswathi.jpg","காயத்ரி","Gayatri — star lord of Astham"),
 "Chithirai": ("images/g-jaganath.jpg","ஜகந்நாதர்","Jagannatha — star lord of Chithirai"),
 "Swathi":    ("images/g-narasimhar.jpg","நரசிம்மர்","Narasimha — star lord of Swathi"),
 "Visakam":   ("images/g-murugar.jpg","முருகன்","Murugan — star lord of Visakam"),
 "Anusham":   ("images/g-periyavaa.jpg","மகா பெரியவா","Kanchi Maha Periyava — star lord of Anusham"),
 "Kettai":    ("images/g-vishnu.jpg","வராஹ பெருமாள்","Varaha Perumal — star lord of Kettai"),
 "Moolam":    ("images/g-hanumar.jpg","ஆஞ்சநேயர்","Hanuman — star lord of Moolam"),
 "Pooradam":  ("images/g-shiva.jpg","ஜம்புகேஸ்வரர்","Jambukeswarar — star lord of Pooradam"),
 "Uttiradam": ("images/g-ganesh.jpg","விநாயகர்","Vinayaka — star lord of Uttiradam"),
 "Thiruvonam":("images/g-hayagreevar.jpg","ஹயக்ரீவர்","Hayagreeva — star lord of Thiruvonam"),
 "Avittam":   ("images/g-vishnu.jpg","அனந்த சயனர்","Anantha Padmanabha — star lord of Avittam"),
 "Sadhayam":  ("images/g-shiva.jpg","மிருத்யுஞ்ஜயர்","Mrityunjaya — star lord of Sadhayam"),
 "Poorattathi":("images/g-sarabeswarar.jpg","சரபேஸ்வரர்","Sarabeswarar — star lord of Poorattathi"),
 "Uttirattathi":("images/g-shiva.jpg","மகா ஈஸ்வரர்","Maheswara — star lord of Uttirattathi"),
 "Revathi":   ("images/g-vishnu.jpg","அரங்கநாதன்","Ranganatha — star lord of Revathi"),
}

# Worthy daily reflections for non-occasion days — rotate by weekday so it never feels flat.
# Each: (tamil, english). Themed to the day's star deity where possible via {deity}.
DAILY_BLESSINGS = [
 ("இன்று {deity} அருள் நிறை நாள். ஒரு விளக்கேற்றி வணங்குங்கள்.","Today is blessed by {deity}. Light a lamp and offer a quiet prayer."),
 ("{deity} துணையுடன் இந்நாள் அமைதியாக அமையட்டும்.","May {deity} keep this day calm and full of grace."),
 ("இன்றைய நட்சத்திரத் தெய்வம் {deity}. மனம் அமைதி கொள்ளட்டும்.","{deity} presides over today's star — may your mind rest in peace."),
 ("{deity} நினைவுடன் நல்லதொரு நாளைத் தொடங்குங்கள்.","Begin the day well, holding {deity} in your heart."),
 ("இந்நாள் {deity} அருளால் சுபமாக அமையட்டும்.","May {deity}'s grace make this an auspicious day."),
]

# Proper descriptions for each FESTIVAL occasion (keyed by tag). The occasion owns the card.
OCCASION_DESC = {
 "ekadasi": ("பெருமாளை நினைத்து விரதம் இருக்க உகந்த புனித நாள்.","A sacred fasting day devoted to Perumal (Vishnu)."),
 "pradosham": ("பிரதோஷ காலத்தில் சிவனை வழிபட மிக உகந்த நாள்.","An auspicious Shiva evening — worship at pradosha twilight."),
 "shivaratri": ("சிவனை இரவு முழுவதும் வழிபடும் மாத சிவராத்திரி.","Maasa Shivaratri — a night of devotion to Lord Shiva."),
 "pournami": ("முழு நிலவு நாள் — அம்மனை வழிபட உகந்த புண்ணிய நாள்.","Full-moon day — auspicious for worship and gratitude."),
 "amavasai": ("முன்னோர்களை நினைத்து தர்ப்பணம் செய்யும் அமாவாசை.","New-moon day to remember and honour the ancestors."),
 "chaturthi": ("விநாயகரை வழிபட்டு இடையூறுகள் நீங்கும் சதுர்த்தி.","Chaturthi — worship Ganesha to clear all obstacles."),
 "sashti": ("முருகப்பெருமானை வழிபடும் சஷ்டி விரத நாள்.","Sashti — a day of devotion to Lord Murugan."),
 "krithigai": ("முருகனுக்குரிய கார்த்திகை நட்சத்திர புண்ணிய நாள்.","Krithigai — sacred to Lord Murugan, light the lamps."),
 "pooram": ("ஆண்டாள் அவதரித்த ஆடிப் பூர புண்ணிய நாள்.","Aadi Pooram — the sacred day Aandaal was born."),
 "amman": ("அம்மனை வழிபட உகந்த ஆடி/தை வெள்ளிக்கிழமை.","An auspicious Friday to worship the Divine Mother."),
 "chevvai": ("அம்மனை வழிபட உகந்த செவ்வாய்க்கிழமை.","An auspicious Tuesday to worship the Divine Mother."),
 "aadi-perukku": ("நீர்வளம் போற்றும் ஆடிப் பெருக்கு நல்நாள்.","Aadi Perukku — honouring the life-giving waters."),
 "onam": ("மகாபலியை வரவேற்கும் திருவோண புண்ணிய நாள்.","Thiruvonam — the sacred Onam day of Mahabali's return."),
 "krishna": ("கண்ணன் அவதரித்த கிருஷ்ண ஜெயந்தி புனித நாள்.","Krishna Jayanthi — the birth of Lord Krishna."),
 "rama": ("ஸ்ரீ ராமர் அவதரித்த ராம நவமி புண்ணிய நாள்.","Sri Rama Navami — the birth of Lord Rama."),
 "hanuman": ("அனுமன் அவதரித்த புண்ணிய ஜயந்தி நாள்.","Hanuman Jayanthi — the birth of Lord Anjaneya."),
 "guru": ("வைகாசி விசாகம் — குருவை வழிபடும் புண்ணிய நாள்.","Vaikasi Visakam — a day to honour the guru."),
}

def occasions(y,m,d, me, dn, wd, nak_en):
    o = []
    ti,_ = tithi(y,m,d)
    if ti in (10,25): o.append(("ekadasi","ஏகாதசி","Ekadasi","perumal"))
    if ti in (12,27): o.append(("pradosham","பிரதோஷம்","Pradosham","shiva"))
    if ti == 14: o.append(("pournami","பௌர்ணமி","Pournami","full-moon"))
    if ti == 29: o.append(("amavasai","அமாவாசை","Amavasai","new-moon"))
    if ti == 18: o.append(("chaturthi","சங்கடஹர சதுர்த்தி","Sankatahara Chaturthi","modak"))
    if ti in (5,20): o.append(("sashti","சஷ்டி","Sashti","vel"))
    if ti == 28: o.append(("shivaratri","மாத சிவராத்திரி","Maasa Shivaratri","shiva"))
    if nak_en == "Krithigai": o.append(("krithigai","கார்த்திகை","Krithigai","lamp"))
    if me == "Aadi" and nak_en == "Pooram": o.append(("pooram","ஆடிப் பூரம்","Aadi Pooram (Aandaal)","amman"))
    if me == "Avani" and nak_en == "Thiruvonam": o.append(("onam","திருவோணம்","Thiruvonam","perumal"))
    if me in ("Aadi","Thai") and wd == 4:
        lab = "ஆடி வெள்ளி" if me=="Aadi" else "தை வெள்ளி"
        o.append(("amman",lab,f"{me} Velli","amman"))
    if me == "Aadi" and dn == 18: o.append(("aadi-perukku","ஆடிப் பெருக்கு","Aadi Perukku","river"))
    # --- Major festivals (nakshatram + month based) ---
    # Krishna Jayanthi (Gokulashtami): Avani, Rohini nakshatram, Krishna paksha
    if me == "Avani" and nak_en == "Rohini":
        o.append(("krishna","கிருஷ்ண ஜயந்தி","Krishna Jayanthi","perumal"))
    # Sri Rama Navami is handled as a fixed festival (Chithirai Shukla Navami) — see FIXED_FESTIVALS
    # Hanuman Jayanthi: Margazhi, Moolam nakshatram (Tamil tradition)
    if me == "Margazhi" and nak_en == "Moolam":
        o.append(("hanuman","அனுமன் ஜயந்தி","Hanuman Jayanthi","vel"))
    # Guru Purnima: Aani/Aadi Pournami with knowledge focus (Aadi Pournami already caught by tithi;
    # tag Vaikasi Visakam as a guru/knowledge day)
    if me == "Vaikasi" and nak_en == "Visakam":
        o.append(("guru","வைகாசி விசாகம்","Vaikasi Visakam","perumal"))
    return o

# Temple-finder mapping: occasion tag -> (search query, Tamil label, English label).
# Used to offer "find the nearest <deity> temple" on relevant days.
# Query terms chosen to return good Google Maps results in Tamil regions & diaspora.
TEMPLE = {
 "ekadasi":   ("Perumal Vishnu temple","பெருமாள் கோயில்","Perumal temple"),
 "onam":      ("Perumal Vishnu temple","பெருமாள் கோயில்","Perumal temple"),
 "pradosham": ("Shiva temple","சிவன் கோயில்","Shiva temple"),
 "shivaratri":("Shiva temple","சிவன் கோயில்","Shiva temple"),
 "pournami":  ("temple","கோயில்","temple"),
 "chaturthi": ("Vinayagar Ganesha temple","விநாயகர் கோயில்","Vinayagar temple"),
 "sashti":    ("Murugan temple","முருகன் கோயில்","Murugan temple"),
 "krithigai": ("Murugan temple","முருகன் கோயில்","Murugan temple"),
 "karthigai": ("Murugan Shiva temple","முருகன் கோயில்","Murugan temple"),
 "amman":     ("Amman Devi temple","அம்மன் கோயில்","Amman temple"),
 "chevvai":   ("Amman Devi temple","அம்மன் கோயில்","Amman temple"),
 "pooram":    ("Aandaal Perumal temple","ஆண்டாள் கோயில்","Aandaal temple"),
 "krishna":   ("Krishna temple","கிருஷ்ணன் கோயில்","Krishna temple"),
 "rama":      ("Rama temple","ராமர் கோயில்","Rama temple"),
 "hanuman":   ("Hanuman Anjaneyar temple","அனுமன் கோயில்","Hanuman temple"),
 "guru":      ("temple","கோயில்","temple"),
 "deepavali": ("temple","கோயில்","temple"),
 "pongal":    ("Surya temple","சூரியன் கோயில்","Surya temple"),
 "puthandu":  ("temple","கோயில்","temple"),
 "ayyappa":   ("Ayyappan temple","ஐயப்பன் கோயில்","Ayyappan temple"),
 "hanuman-tamil": ("Hanuman Anjaneyar temple","அனுமன் கோயில்","Hanuman temple"),
 "narasimha": ("Narasimha Perumal temple","நரசிம்மர் கோயில்","Narasimha temple"),
 "balaji":    ("Balaji Venkateswara temple","பாலாஜி கோயில்","Balaji temple"),
 "meenakshi": ("Meenakshi Amman temple","மீனாட்சி அம்மன் கோயில்","Meenakshi temple"),
 "varalakshmi": ("Lakshmi temple","லட்சுமி கோயில்","Lakshmi temple"),
 "upakarma": ("Vishnu Perumal temple","பெருமாள் கோயில்","Perumal temple"),
 "karadaiyan": ("Amman temple","அம்மன் கோயில்","Amman temple"),
 "akshaya": ("Lakshmi temple","லட்சுமி கோயில்","Lakshmi temple"),
 "kamakshi": ("Kamakshi Amman temple","காமாட்சி அம்மன் கோயில்","Kamakshi temple"),
}

# Listen-finder: occasion tag -> (YouTube search query, Tamil stotram name, English name).
# Canonical devotional works (not playlists) — the RIGHT stotram for THIS observance.
AUDIO = {
 "ekadasi":   ("Vishnu Sahasranamam","விஷ்ணு சஹஸ்ரநாமம்","Vishnu Sahasranamam"),
 "onam":      ("Vishnu Sahasranamam","விஷ்ணு சஹஸ்ரநாமம்","Vishnu Sahasranamam"),
 "pradosham": ("Lingashtakam","லிங்காஷ்டகம்","Lingashtakam"),
 "shivaratri":("Shiva Panchakshara Stotram","சிவ பஞ்சாக்ஷரம்","Shiva Panchaksharam"),
 "pournami":  ("Om Namah Shivaya chant","ஓம் நமசிவாய","Om Namah Shivaya"),
 "chaturthi": ("Vinayagar Agaval","விநாயகர் அகவல்","Vinayagar Agaval"),
 "sashti":    ("Kandha Sashti Kavasam","கந்த சஷ்டி கவசம்","Kandha Sashti Kavasam"),
 "krithigai": ("Kandha Sashti Kavasam","கந்த சஷ்டி கவசம்","Kandha Sashti Kavasam"),
 "karthigai": ("Thiruppugazh Murugan","திருப்புகழ்","Thiruppugazh"),
 "amman":     ("Abirami Andhadhi","அபிராமி அந்தாதி","Abirami Andhadhi"),
 "chevvai":   ("Abirami Andhadhi","அபிராமி அந்தாதி","Abirami Andhadhi"),
 "pooram":    ("Thiruppavai Andal","திருப்பாவை","Thiruppavai"),
 "krishna":   ("Krishna Bhajans Tamil","கிருஷ்ண பஜனை","Krishna bhajans"),
 "rama":      ("Sri Rama Bhajans","ஸ்ரீ ராம பஜனை","Rama bhajans"),
 "hanuman":   ("Hanuman Chalisa","அனுமன் சாலீசா","Hanuman Chalisa"),
 "guru":      ("Guru Stotram","குரு ஸ்தோத்திரம்","Guru Stotram"),
 "deepavali": ("Lakshmi Ashtakam","லக்ஷ்மி அஷ்டகம்","Lakshmi Ashtakam"),
 "pongal":    ("Suryashtakam Surya Stotram","சூரிய அஷ்டகம்","Suryashtakam"),
 "puthandu":  ("Ganesha Pancharatnam","கணேச பஞ்சரத்னம்","Ganesha Pancharatnam"),
 "ayyappa":   ("Harivarasanam Ayyappan","ஹரிவராசனம்","Harivarasanam"),
 "hanuman-tamil": ("Hanuman Chalisa","அனுமன் சாலீசா","Hanuman Chalisa"),
 "narasimha": ("Narasimha Kavacham","நரசிம்ம கவசம்","Narasimha Kavacham"),
 "balaji":    ("Venkatesa Suprabhatam","வேங்கடேச சுப்ரபாதம்","Venkatesa Suprabhatam"),
 "meenakshi": ("Meenakshi Pancharatnam","மீனாட்சி பஞ்சரத்னம்","Meenakshi Pancharatnam"),
 "varalakshmi": ("Sri Varalakshmi Ashtakam","வரலட்சுமி அஷ்டகம்","Varalakshmi Ashtakam"),
 "upakarma": ("Vishnu Sahasranamam","விஷ்ணு சஹஸ்ரநாமம்","Vishnu Sahasranamam"),
 "karadaiyan": ("Savitri Gowri Stotram","கௌரி ஸ்தோத்திரம்","Gowri Stotram"),
 "akshaya": ("Sri Lakshmi Ashtakam","லட்சுமி அஷ்டகம்","Lakshmi Ashtakam"),
 "kamakshi": ("Kamakshi Suprabhatam","காமாட்சி ஸ்தோத்திரம்","Kamakshi Stotram"),
}

# Per-star-deity audio for plain days, by deity image (mirrors STAR_TEMPLE).
STAR_AUDIO = {
 "g-vishnu.jpg":      ("Vishnu Sahasranamam","விஷ்ணு சஹஸ்ரநாமம்","Vishnu Sahasranamam"),
 "g-shiva.jpg": ("Lingashtakam","லிங்காஷ்டகம்","Lingashtakam"),
 "g-murugar.jpg":     ("Kandha Sashti Kavasam","கந்த சஷ்டி கவசம்","Kandha Sashti Kavasam"),
 "g-durga.jpg":       ("Abirami Andhadhi","அபிராமி அந்தாதி","Abirami Andhadhi"),
 "new-lakshmi.jpg":     ("Lakshmi Ashtakam","லக்ஷ்மி அஷ்டகம்","Lakshmi Ashtakam"),
 "g-saraswathi.jpg":   ("Saraswati Vandana","சரஸ்வதி வந்தனம்","Saraswati Vandana"),
 "g-krishna.jpg":     ("Krishna Bhajans Tamil","கிருஷ்ண பஜனை","Krishna bhajans"),
 "g-rama.jpg":        ("Sri Rama Bhajans","ஸ்ரீ ராம பஜனை","Rama bhajans"),
 "g-hanumar.jpg":     ("Hanuman Chalisa","அனுமன் சாலீசா","Hanuman Chalisa"),
 "g-ganesh.jpg":     ("Vinayagar Agaval","விநாயகர் அகவல்","Vinayagar Agaval"),
 "new-aandaal.jpg":     ("Thiruppavai Andal","திருப்பாவை","Thiruppavai"),
 "new-naga.jpg":        ("Nagar Stotram","நாக ஸ்தோத்திரம்","Naga Stotram"),
 "new-surya.jpg":       ("Suryashtakam Surya Stotram","சூரிய அஷ்டகம்","Suryashtakam"),
  "g-jaganath.jpg":    ("Vishnu Sahasranamam","விஷ்ணு சஹஸ்ரநாமம்","Vishnu Sahasranamam"),
 "g-sarabeswarar.jpg":("Lingashtakam","லிங்காஷ்டகம்","Lingashtakam"),
 "g-abirami.jpg":     ("Abirami Andhadhi","அபிராமி அந்தாதி","Abirami Andhadhi"),
 "g-periyavaa.jpg":    ("Maha Periyava Bhajan","மகா பெரியவா பஜனை","Maha Periyava bhajan"),
}

# ---- Fixed-date major festivals (specific calendar days, verified from Tamil panchangam sources) ----
# Each: date -> (tag, tamil, english, image_key). These are added as festival occasions.
FIXED_FESTIVALS = {
 # 2026
 "2026-09-04": ("krishna","கிருஷ்ண ஜயந்தி","Krishna Jayanthi","krishna"),
 "2026-09-14": ("chaturthi","விநாயகர் சதுர்த்தி","Vinayaka Chaturthi","chaturthi"),
 "2026-08-26": ("onam","திருவோணம் (ஓணம்)","Thiruvonam (Onam)","onam"),
 "2026-10-11": ("amman","நவராத்திரி ஆரம்பம்","Navaratri begins","kamakshi"),
 "2026-10-19": ("amman","சரஸ்வதி பூஜை","Saraswati Pooja","guru"),
 "2026-10-20": ("amman","விஜயதசமி · ஆயுத பூஜை","Vijayadashami · Ayudha Pooja","amman"),
 "2026-11-08": ("deepavali","தீபாவளி","Deepavali","deepavali"),
 "2026-11-15": ("sashti","சூர சம்ஹாரம் · கந்த சஷ்டி","Soora Samharam · Skanda Sashti","sashti"),
 "2026-11-24": ("karthigai","கார்த்திகை தீபம்","Karthigai Deepam","karthigai"),
 "2026-12-20": ("ekadasi","வைகுண்ட ஏகாதசி","Vaikunta Ekadasi","ekadasi"),
 "2026-12-24": ("shivaratri","ஆருத்ரா தரிசனம்","Arudra Darshan","shivaratri"),
 # 2027
 "2027-01-14": ("pongal","போகி","Bhogi","pongal"),
 "2027-01-15": ("pongal","தைப் பொங்கல்","Thai Pongal","pongal"),
 "2027-01-16": ("pongal","மாட்டுப் பொங்கல்","Mattu Pongal","pongal"),
 "2027-01-17": ("pongal","காணும் பொங்கல்","Kaanum Pongal","pongal"),
 "2027-01-22": ("sashti","தைப்பூசம்","Thaipusam","sashti"),
 "2027-02-20": ("amman","மாசி மகம்","Maasi Magam","kamakshi"),
 "2027-03-06": ("shivaratri","மகா சிவராத்திரி","Maha Shivaratri","shivaratri"),
 "2027-03-22": ("pooram","பங்குனி உத்திரம்","Panguni Uthiram","amman"),
 "2027-04-14": ("puthandu","தமிழ்ப் புத்தாண்டு","Tamil New Year (Puthandu)","surya"),
 "2027-05-20": ("guru","வைகாசி விசாகம்","Vaikasi Visakam","guru"),
 # New deity festivals (Part B) — dates computed via Swiss Ephemeris / verified
 "2026-11-16": ("ayyappa","மண்டல பூஜை ஆரம்பம்","Mandala Pooja begins (Ayyappan)","ayyappa"),
 "2027-01-07": ("hanuman-tamil","ஹனுமத் ஜயந்தி","Hanumath Jayanthi","hanuman"),
 "2027-05-19": ("narasimha","நரசிம்ம ஜயந்தி","Narasimha Jayanthi","narasimha"),
 "2027-04-15": ("rama","ஸ்ரீ ராம நவமி","Sri Rama Navami","rama"),
 "2026-10-31": ("balaji","திருப்பதி ப்ரம்மோற்சவம்","Tirupati Brahmotsavam","balaji"),
 "2027-04-21": ("meenakshi","மீனாட்சி திருக்கல்யாணம்","Meenakshi Thirukalyanam","meenakshi"),
 # Additional in-range festivals (verified: drikpanchang / prokerala / Kanchi Kamakoti)
 "2026-08-21": ("varalakshmi","வரலட்சுமி விரதம்","Varalakshmi Vratham","lakshmi"),
 "2026-08-27": ("upakarma","ஆவணி அவிட்டம் · உபாகர்மம்","Avani Avittam (Upakarma)","vishnu"),
 "2026-10-10": ("mahalaya","மகாளய அமாவாசை","Mahalaya Amavasai","amavasai-img"),
 "2027-03-15": ("karadaiyan","காரடையான் நோன்பு","Karadaiyan Nombu","durga"),
 "2027-05-09": ("akshaya","அட்சய திருதியை","Akshaya Tritiya","lakshmi"),
}
FIXED_DESC = {
 "deepavali": ("ஒளியின் திருநாள் — தீபாவளி நல்வாழ்த்துக்கள்.","Deepavali — the festival of lights and new beginnings."),
 "karthigai": ("வீடு முழுவதும் அகல் விளக்கேற்றும் கார்த்திகை தீபம்.","Karthigai Deepam — light every lamp at home and temple."),
 "pongal": ("சூரியனை வணங்கி நன்றி கூறும் அறுவடைத் திருநாள்.","Pongal — the harvest thanksgiving to Surya."),
 "puthandu": ("புதிய தமிழ் ஆண்டின் முதல் நாள் — புத்தாண்டு வாழ்த்துக்கள்.","Tamil New Year — a fresh start, Puthandu vazhthukkal."),
 "ayyappa": ("ஐயப்பனை வழிபடும் மண்டல கால புண்ணிய நாள்.","A sacred day of the Ayyappa Mandala season."),
 "hanuman-tamil": ("அனுமன் அவதரித்த தமிழ் ஹனுமத் ஜயந்தி.","Tamil Hanumath Jayanthi — the birth of Lord Anjaneya."),
 "narasimha": ("விஷ்ணுவின் நரசிம்ம அவதார புண்ணிய தினம்.","Narasimha Jayanthi — Vishnu's man-lion avatar."),
 "balaji": ("திருப்பதி வேங்கடேசப் பெருமாள் ப்ரம்மோற்சவம்.","Tirupati Balaji Brahmotsavam — the festival of Venkateswara."),
 "meenakshi": ("மதுரை மீனாட்சி–சுந்தரேஸ்வரர் திருக்கல்யாணம்.","The celestial wedding of Madurai Meenakshi & Sundareswarar."),
 "varalakshmi": ("செல்வம் அருளும் வரலட்சுமியை வழிபடும் விரதம்.","Varalakshmi Vratham — worship of the boon-granting Lakshmi."),
 "upakarma": ("புதிய பூணூல் அணியும் ஆவணி அவிட்ட உபாகர்ம நாள்.","Avani Avittam — the sacred Upakarma / thread-changing day."),
 "mahalaya": ("முன்னோர்களை நினைந்து தர்ப்பணம் செய்யும் மகாளய அமாவாசை.","Mahalaya Amavasai — remembrance and tarpanam for ancestors."),
 "karadaiyan": ("மங்கல்யப் பாதுகாப்பிற்காக பெண்கள் நோற்கும் நோன்பு.","Karadaiyan Nombu — women's vratam for marital well-being."),
 "akshaya": ("அழியாத செல்வம் தரும் அட்சய திருதியை புண்ணிய நாள்.","Akshaya Tritiya — an auspicious day of unending prosperity."),
}

# extra image keys used only by fixed festivals
PHOTO["deepavali"] = ("images/g-deepavali.jpg","")
PHOTO["karthigai"] = ("images/new-karthigai-deepam.jpg","")
PHOTO["pongal"]    = ("images/new-pongal.jpg","")
PHOTO["puthandu"]  = ("images/new-pongal.jpg","")
PHOTO["surya"]     = ("images/new-surya.jpg","")
# new deity festival images (Part B)
PHOTO["ayyappa"]   = ("images/g-aiyappa.jpg","")
PHOTO["narasimha"] = ("images/g-narasimhar.jpg","")
PHOTO["balaji"]    = ("images/g-balaji.jpg","")
PHOTO["meenakshi"] = ("images/g-meenakshi.jpg","")
PHOTO["lakshmi"]   = ("images/new-lakshmi.jpg","")
PHOTO["naga"]      = ("images/new-naga.jpg","")
PHOTO["vishnu"]    = ("images/g-vishnu.jpg","")
PHOTO["durga"]     = ("images/g-durga.jpg","")
PHOTO["amavasai-img"] = ("images/g-amavasai.jpg","")
PHOTO["kamakshi"]  = ("images/g-kamakshi.jpg","")

# ---- Pambu Panchangam overrides (Vakyam) — these WIN. Add dates as you verify them. ----
OVERRIDES = {
 "2026-07-24": {"nakshatra":"அனுஷம்","nakshatraEn":"Anusham","confidence":"verified","source":"Pambu Panchangam (Aadi 8) — confirmed"},
 "2026-07-26": {"tags":["pradosham"],"title":"பிரதோஷம்","titleEn":"Pradosham","icon":"shiva","photo":"images/g-shiva.jpg","oneLiner":"பிரதோஷ காலத்தில் சிவனை வழிபட மிக உகந்த நாள்.","oneLinerEn":"An auspicious Shiva evening — worship at pradosha twilight.","always":True,"confidence":"verified","source":"Pambu Panchangam (Aadi 10)"},
 "2026-07-28": {"tags":["pournami"],"title":"ஆடி பௌர்ணமி","titleEn":"Aadi Pournami","icon":"full-moon","photo":"images/g-pournami.jpg","oneLiner":"முழு நிலவு நாள் — வழிபாட்டிற்கு உகந்த ஆடிப் பௌர்ணமி.","oneLinerEn":"Aadi full-moon day — auspicious for worship and gratitude.","always":True,"confidence":"verified","source":"Pambu Panchangam (Aadi 12, circled)"},
 "2026-08-12": {"tags":["amavasai"],"title":"ஆடி அமாவாசை","titleEn":"Aadi Amavasai","icon":"new-moon","photo":"images/g-amavasai.jpg","oneLiner":"முன்னோர்களை நினைத்து தர்ப்பணம் செய்யும் ஆடி அமாவாசை.","oneLinerEn":"Aadi new-moon — a day to honour the ancestors.","always":True,"confidence":"verified","source":"Pambu Panchangam (Aadi 27, circled)"},
}

def build(start, end):
    days = []
    d = start
    idx = 0
    while d <= end:
        mn, me, dn = tamil_md(d.year,d.month,d.day)
        ni,nta,nen = nak(d.year,d.month,d.day)
        ti,tta = tithi(d.year,d.month,d.day)
        occ = occasions(d.year,d.month,d.day, me, dn, d.weekday(), nen)
        e = {"date":d.isoformat(),"tamilMonth":mn,"tamilMonthEn":me,"tamilDay":dn,
             "weekdayFull":WEEKDAYS_TA[d.weekday()],"nakshatra":nta,"nakshatraEn":nen,
             "tithi":tta,"confidence":"derived",
             "source":"Drik-ganita (Swiss Ephemeris, Lahiri ayanamsa)"}
        e["bands"] = time_bands(d.year, d.month, d.day)
        # Muhurtham (auspicious for weddings/functions): favourable nakshatram + tithi + weekday.
        # Classical marriage-friendly stars, waxing-friendly tithis, avoiding Tue/Sat & inauspicious tithis.
        MUHURTHAM_STARS = {"Rohini","Mrigasheersham","Magam","Uttiram","Astham","Swathi",
                           "Anusham","Moolam","Uttiradam","Thiruvonam","Uttirattathi","Revathi"}
        _good_tithi = ti not in (3,8,13,14,18,23,28,29)  # avoid Chaturthi/Navami/Chaturdashi/Amavasai/etc
        _good_wd = d.weekday() not in (1,5)  # avoid Tue, Sat
        if nen in MUHURTHAM_STARS and _good_tithi and _good_wd and me not in ("Aadi","Purattasi"):
            # Aadi & Purattasi traditionally avoided for muhurthams
            e["muhurtham"] = True
        # star deity for this day (every day gets one)
        star = NAK_DEITY.get(nen)
        # Always record the star deity so the UI can show it even on festival days.
        if star:
            e["starImage"] = star[0]
            e["starDeity"] = star[1]
            e["starCredit"] = star[2]
        fixed = FIXED_FESTIVALS.get(d.isoformat())
        if fixed:
            # a major named festival on a fixed date — it owns the card
            ftag, fta, fen, fkey = fixed
            e["tags"] = [ftag]
            e["title"] = fta
            e["titleEn"] = fen
            e["icon"] = ftag
            if fkey in PHOTO: e["photo"] = PHOTO[fkey][0]
            elif star: e["photo"] = star[0]
            desc = FIXED_DESC.get(ftag) or FIXED_DESC.get(fkey) or OCCASION_DESC.get(ftag)
            if desc: e["oneLiner"], e["oneLinerEn"] = desc
            e["always"] = True
            e["major"] = True
            if ftag in TEMPLE:
                tq, tta, ten = TEMPLE[ftag]
                e["temple"] = {"q": tq, "ta": tta, "en": ten}
            if ftag in AUDIO:
                aq, ata, aen = AUDIO[ftag]
                e["audio"] = {"q": aq, "ta": ata, "en": aen}
        elif occ:
            lead = min(occ, key=lambda o: PRIO.index(o[0]) if o[0] in PRIO else 99)
            e["tags"] = [o[0] for o in occ]
            e["title"] = " · ".join(dict.fromkeys(o[1] for o in occ))
            e["titleEn"] = " · ".join(dict.fromkeys(o[2] for o in occ))
            e["icon"] = lead[3]
            if lead[0] in PHOTO: e["photo"],_ = PHOTO[lead[0]]
            elif star: e["photo"] = star[0]
            # the occasion owns the card — give it a proper description, not the star blessing
            desc = OCCASION_DESC.get(lead[0])
            if desc:
                e["oneLiner"], e["oneLinerEn"] = desc
            e["always"] = lead[0] in ("ekadasi","amavasai","pournami","pooram","aadi-perukku")
            if lead[0] in TEMPLE:
                tq, tta, ten = TEMPLE[lead[0]]
                e["temple"] = {"q": tq, "ta": tta, "en": ten}
            if lead[0] in AUDIO:
                aq, ata, aen = AUDIO[lead[0]]
                e["audio"] = {"q": aq, "ta": ata, "en": aen}
        else:
            e["tags"] = []
            # non-occasion day: show the star's presiding deity + a worthy blessing
            if star:
                img, deity_ta, credit = star
                e["photo"] = img
                e["photoCredit"] = credit
                e["starDeity"] = deity_ta
                bt, ben = DAILY_BLESSINGS[idx % len(DAILY_BLESSINGS)]
                e["title"] = deity_ta + " அருள் நாள்"
                e["titleEn"] = deity_ta + "'s blessing"
                e["oneLiner"] = bt.replace("{deity}", deity_ta)
                e["oneLinerEn"] = ben.replace("{deity}", credit.split(" — ")[0])
                e["daily"] = True   # flag: a reflective day, not a festival
                # temple link for the star deity of a plain day, by its image
                STAR_TEMPLE = {
                    "g-vishnu.jpg":("Perumal Vishnu temple","பெருமாள் கோயில்","Perumal temple"),
                    "g-shiva.jpg":("Shiva temple","சிவன் கோயில்","Shiva temple"),
                    "g-murugar.jpg":("Murugan temple","முருகன் கோயில்","Murugan temple"),
                    "g-durga.jpg":("Amman Devi temple","அம்மன் கோயில்","Amman temple"),
                    "new-lakshmi.jpg":("Lakshmi temple","லட்சுமி கோயில்","Lakshmi temple"),
                    "g-saraswathi.jpg":("Saraswati temple","சரஸ்வதி கோயில்","Saraswati temple"),
                    "g-krishna.jpg":("Krishna temple","கிருஷ்ணன் கோயில்","Krishna temple"),
                    "g-rama.jpg":("Rama temple","ராமர் கோயில்","Rama temple"),
                    "g-hanumar.jpg":("Hanuman Anjaneyar temple","அனுமன் கோயில்","Hanuman temple"),
                    "g-ganesh.jpg":("Vinayagar Ganesha temple","விநாயகர் கோயில்","Vinayagar temple"),
                    "new-aandaal.jpg":("Aandaal Perumal temple","ஆண்டாள் கோயில்","Aandaal temple"),
                    "new-naga.jpg":("Naga temple","நாகர் கோயில்","Naga temple"),
                    "new-surya.jpg":("Surya temple","சூரியன் கோயில்","Surya temple"),
                    "g-jaganath.jpg":("Perumal Vishnu temple","பெருமாள் கோயில்","Perumal temple"),
                    "g-sarabeswarar.jpg":("Shiva temple","சிவன் கோயில்","Shiva temple"),
                    "g-abirami.jpg":("Amman Devi temple","அம்மன் கோயில்","Amman temple"),
                    "g-periyavaa.jpg":("Kanchi Mutt","காஞ்சி மடம்","Kanchi Mutt"),
                }
                _base = os.path.basename(img)
                if _base in STAR_TEMPLE:
                    tq,tta,ten = STAR_TEMPLE[_base]
                    e["temple"] = {"q": tq, "ta": tta, "en": ten}
                if _base in STAR_AUDIO:
                    aq,ata,aen = STAR_AUDIO[_base]
                    e["audio"] = {"q": aq, "ta": ata, "en": aen}
        days.append(e); d += datetime.timedelta(days=1); idx += 1
    return days

# Specific hand-verified links, applied to ANY day whose image matches.
# videoId -> plays that exact YouTube video in one click (falls back to search if absent).
# mapUrl  -> opens that exact Google Maps place (falls back to search query if absent).
SPECIAL_AUDIO_VIDEO = {
 "g-periyavaa.jpg": "PpGDBkOFSBI",   # Maha Periyava bhajan — user-verified
}
SPECIAL_TEMPLE_URL = {
 "g-periyavaa.jpg": "https://www.google.com/maps/place/Sri+Maha+Periyava+%26+Sivan+Sar+Mani+mandapam/@10.9549375,75.8834336,8z/data=!4m10!1m2!2m1!1smaha+periyava+temple!3m6!1s0x3baa31d6b3603921:0x8a7030eecafecf9b!8m2!3d10.9549375!4d78.1905625!15sChRtYWhhIHBlcml5YXZhIHRlbXBsZVoWIhRtYWhhIHBlcml5YXZhIHRlbXBsZZIBDGhpbmR1X3RlbXBsZZoBJENoZERTVWhOTUc5blMwVkpRMEZuVFVOWk5tWmZUV3BCUlJBQuABAPoBBAgAEB8!16s%2Fg%2F11xcljw7sd",
}
def apply_special_links(days):
    for e in days:
        img = e.get("photo","")
        base = os.path.basename(img)
        if base in SPECIAL_AUDIO_VIDEO and e.get("audio"):
            e["audio"]["videoId"] = SPECIAL_AUDIO_VIDEO[base]
        if base in SPECIAL_TEMPLE_URL and e.get("temple"):
            e["temple"]["url"] = SPECIAL_TEMPLE_URL[base]
    return days

def main():
    start = datetime.date(2026,7,17); end = datetime.date(2027,7,16)
    days = build(start,end)
    by = {x["date"]:x for x in days}
    ovfile = os.path.join(os.path.dirname(__file__),"overrides.json")
    ov = dict(OVERRIDES)
    if os.path.exists(ovfile):
        try:
            fileov = json.load(open(ovfile)); ov.update({k:v for k,v in fileov.items() if not k.startswith("_")})
        except Exception as ex: print("overrides.json skipped:", ex)
    n=0
    for date,patch in ov.items():
        if date in by:
            # an override promotes a day to a festival — clear any daily-blessing residue
            if "tags" in patch or "title" in patch:
                for k in ("daily","photoCredit","starDeity","temple","audio"):
                    by[date].pop(k, None)
            by[date].update(patch)
            # recompute the temple link from the override's lead tag
            _tags = by[date].get("tags") or []
            if _tags and _tags[0] in TEMPLE:
                tq,tta,ten = TEMPLE[_tags[0]]
                by[date]["temple"] = {"q": tq, "ta": tta, "en": ten}
            if _tags and _tags[0] in AUDIO:
                aq,ata,aen = AUDIO[_tags[0]]
                by[date]["audio"] = {"q": aq, "ta": ata, "en": aen}
            n+=1
    apply_special_links(days)
    out = {
      "meta":{"tamilYear":"பரபாவ","tamilYearFull":"ஸ்ரீ பரபாவ வருடம்","kaliyugam":5127,"generated":str(datetime.date.today()),
              "engine":"Drik-ganita (Swiss Ephemeris / Lahiri) + Pambu Panchangam overrides",
              "monthAnchors":[{"tamilMonth":"ஆடி","tamilMonthEn":"Aadi","startDate":"2026-07-17","days":32,
                 "source":"Confirmed against physical Pambu Panchangam (Aadi 1 = July 17)"}]},
      "days":days,
      "eventCategories":[
        {"id":"amman","label":"அம்மன் நாட்கள்","labelEn":"Amman days","icon":"amman"},
        {"id":"ekadasi","label":"ஏகாதசி","labelEn":"Ekadasi","icon":"perumal"},
        {"id":"pradosham","label":"பிரதோஷம்","labelEn":"Pradosham","icon":"shiva"},
        {"id":"pournami","label":"பௌர்ணமி","labelEn":"Pournami","icon":"full-moon"},
        {"id":"amavasai","label":"அமாவாசை","labelEn":"Amavasai","icon":"new-moon"},
        {"id":"sashti","label":"சஷ்டி","labelEn":"Sashti","icon":"vel"},
        {"id":"krithigai","label":"கார்த்திகை","labelEn":"Krithigai","icon":"lamp"},
        {"id":"chaturthi","label":"சதுர்த்தி","labelEn":"Chaturthi","icon":"modak"},
        {"id":"pooram","label":"பூரம் (ஆண்டாள்)","labelEn":"Aadi Pooram","icon":"amman"},
        {"id":"shivaratri","label":"சிவராத்திரி","labelEn":"Shivaratri","icon":"shiva"}
      ]
    }
    path = os.path.join(os.path.dirname(__file__),"data.json")
    json.dump(out, open(path,"w"), ensure_ascii=False, indent=1)
    print(f"Wrote {len(days)} days to {path} ({n} Pambu Panchangam overrides applied)")

if __name__ == "__main__":
    main()
