from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QStyle,
                             QSlider, QFrame, QSizePolicy, QSpacerItem, QMainWindow)
import html_parser_cls


html = """
<table role="grid" id="table-short-bingo-prize-breakdown" class="no-footer">

<thead class="Rez_Normal_Center_Txt3">

<tr role="row">

<th class="Rez_Normal_Center_Txt3a">
Добитак
</th>

<th class="Rez_Normal_Center_Txt3b">
Добитници
</th>

<th class="Rez_Normal_Center_Txt3b">
Износ у дин
</th>

</tr>

</thead>

<tbody class="Rez_Normal_Center_Txt4">

<tr role="row">

<td class="Rez_Normal_Center_Txt4a">
Бинго 40+
</td>

<td class="Rez_Normal_Center_Txt4b">
1
</td>

<td class="Rez_Normal_Center_Txt4b">
1.627.804,80
</td>

</tr>

<tr role="row">

<td class="Rez_Normal_Center_Txt4a">
Са 2 реда
</td>

<td class="Rez_Normal_Center_Txt4b">
197
</td>

<td class="Rez_Normal_Center_Txt4b">
4.131,48
</td>

</tr>

<tr role="row">

<td class="Rez_Normal_Center_Txt4a">
Са 1 редом
</td>

<td class="Rez_Normal_Center_Txt4b">
13.678
</td>

<td class="Rez_Normal_Center_Txt4b">
320,00
</td>

</tr>

<tr role="row">

<td class="Rez_Normal_Center_Txt4a">
Замене
</td>

<td class="Rez_Normal_Center_Txt4b">
11.232
</td>

<td class="Rez_Normal_Center_Txt4b">
160,00
</td>

</tr>

</tbody>

</table>
"""

class Proba(QMainWindow):
    def __init__(self, html: str):
        super().__init__()
        self.setWindowTitle("My App")

        self.html = html
        self.resize(1000, 800)

        self.html_parser = html_parser_cls.HtmlParser()

        self.table = self.html_parser.get_PYQT5_table_ver2(
            html_code=self.html,
            parent_widget=self,
            font_size=20

        )

        # self.txt = QLineEdit(self)
        # self.txt.returnPressed.connect(self.return_press)

        self.show()

    # def return_press(self):
    #     print (self.txt.selectedText())

app = QApplication([])
proba = Proba(html)
app.exec_()



LANG_SECTIONS = """
中文 (Chinese) • Français (French) • Deutsch (German) • Ελληνικά (Greek) • Malagasy • Русский (Russian)
•Հայերեն (Armenian) • Català (Catalan) • Čeština (Czech) • Nederlands (Dutch) • Suomi (Finnish) • Español (Spanish) • Esperanto • Eesti (Estonian) • हिन्दी (Hindi) • Magyar (Hungarian) • Ido • Bahasa Indonesia (Indonesian) • Italiano (Italian) • 日本語 (Japanese) • ಕನ್ನಡ (Kannada) • 한국어 (Korean) • Kurdî / كوردی (Kurdish) • Limburgs (Limburgish) • Lietuvių (Lithuanian) • മലയാളം (Malayalam) • မြန်မာဘာသာ (Burmese) • Norsk Bokmål (Norwegian) • ଓଡ଼ିଆ (Odia) • فارسى (Persian) • Polski (Polish) • Português (Portuguese) • Română (Romanian) • Srpskohrvatski (Serbo-Croatian) • Svenska (Swedish) • தமிழ் (Tamil) • తెలుగు (Telugu) • ไทย (Thai) • Türkçe (Turkish) • Tiếng Việt (Vietnamese) • Oʻzbekcha / Ўзбекча (Uzbek)
•Afrikaans • Shqip (Albanian) • العربية (Arabic) • Asturianu (Asturian) • Azərbaycan (Azeri) • Bahasa Melayu (Malay) • Euskara (Basque) • বাংলা (Bengali) • Brezhoneg (Breton) • Български (Bulgarian) • Hrvatski (Croatian) • Dansk (Danish) • Frysk (West Frisian) • Galego (Galician) • ქართული (Georgian) • עברית (Hebrew) • Íslenska (Icelandic) • Basa Jawa (Javanese) • Кыргызча (Kyrgyz) • ລາວ (Lao) • Latina (Latin) • Latviešu (Latvian) • Lombard • Bân-lâm-gú (Min Nan) • ဘာသာမန် (Mon) • Nynorsk (Norwegian) • Occitan • Oromoo (Oromo) • پښتو (Pashto) • ਪੰਜਾਬੀ (Punjabi) • Српски (Serbian) • လိၵ်ႈတႆ (Shan) • Sicilianu (Sicilian) • Simple English • Slovenčina (Slovak) • Kiswahili (Swahili) • Tagalog • Тоҷикӣ (Tajik) • Українська (Ukrainian) • اردو (Urdu) • Volapük • Walon (Walloon) • Cymraeg (Welsh)
•Armãneashce (Aromanian) • Aymara • Беларуская (Belarusian) • Bosanski (Bosnian) • Bikol • Corsu (Corsican) • Føroyskt (Faroese) • Fiji Hindi • Kalaallisut (Greenlandic) • Avañe'ẽ (Guaraní) • Interlingua • Interlingue • Gaeilge (Irish) • كٲشُر (Kashmiri) • Kaszëbsczi (Kashubian) • қазақша (Kazakh) • ភាសាខ្មែរ (Khmer) • Кыргызча (Kyrgyz) • Lëtzebuergesch (Luxembourgish) • Māori • Plattdüütsch (Low Saxon) • Македонски (Macedonian) • Malti (Maltese) • मराठी (Marathi) • Nahuatl • नेपाली (Nepali) • Li Niha (Nias) • Ænglisc (Old English) • Gàidhlig (Scottish Gaelic) • Tacawit (Shawiya) • سنڌي (Sindhi) • සිංහල (Sinhalese) • Slovenščina (Slovene) • Soomaaliga (Somali) • Hornjoserbsce (Upper Sorbian) • seSotho (Southern Sotho) • Basa Sunda (Sundanese) • Tatarça / Татарча (Tatar) • تركمن / Туркмен (Turkmen) • Uyghurche / ئۇيغۇرچە (Uyghur) • پنجابی (Western Punjabi) • Wollof (Wolof) • isiZulu (Zulu)
•አማርኛ (Amharic) • Aragonés (Aragonese) • ᏣᎳᎩ (Cherokee) • Kernewek / Karnuack (Cornish) • ދިވެހިބަސް (Divehi) • ગુજરાતી (Gujarati) • Hausa / هَوُسَ (Hausa) • ʻŌlelo Hawaiʻi (Hawaiian) • ᐃᓄᒃᑎᑐᑦ (Inuktitut) • Ikinyarwanda (Kinyarwanda) • Lingala • Gaelg (Manx) • Монгол (Mongolian) • Runa Simi (Quechua) • Gagana Samoa (Samoan) • Sängö • Setswana • ትግርኛ (Tigrinya) • Tok Pisin • Xitsonga (Tsonga) • ייִדיש (Yiddish)
"""


a1 = "中文 (Chinese) • Français (French) • Deutsch (German) • Ελληνικά (Greek) • Malagasy • Русский (Russian)"
a2 = "Հայերեն (Armenian) • Català (Catalan) • Čeština (Czech) • Nederlands (Dutch) • Suomi (Finnish) • Español (Spanish) • Esperanto • Eesti (Estonian) • हिन्दी (Hindi) • Magyar (Hungarian) • Ido • Bahasa Indonesia (Indonesian) • Italiano (Italian) • 日本語 (Japanese) • ಕನ್ನಡ (Kannada) • 한국어 (Korean) • Kurdî / كوردی (Kurdish) • Limburgs (Limburgish) • Lietuvių (Lithuanian) • മലയാളം (Malayalam) • မြန်မာဘာသာ (Burmese) • Norsk Bokmål (Norwegian) • ଓଡ଼ିଆ (Odia) • فارسى (Persian) • Polski (Polish) • Português (Portuguese) • Română (Romanian) • Srpskohrvatski (Serbo-Croatian) • Svenska (Swedish) • தமிழ் (Tamil) • తెలుగు (Telugu) • ไทย (Thai) • Türkçe (Turkish) • Tiếng Việt (Vietnamese) • Oʻzbekcha / Ўзбекча (Uzbek)"
a3 = "Afrikaans • Shqip (Albanian) • العربية (Arabic) • Asturianu (Asturian) • Azərbaycan (Azeri) • Bahasa Melayu (Malay) • Euskara (Basque) • বাংলা (Bengali) • Brezhoneg (Breton) • Български (Bulgarian) • Hrvatski (Croatian) • Dansk (Danish) • Frysk (West Frisian) • Galego (Galician) • ქართული (Georgian) • עברית (Hebrew) • Íslenska (Icelandic) • Basa Jawa (Javanese) • Кыргызча (Kyrgyz) • ລາວ (Lao) • Latina (Latin) • Latviešu (Latvian) • Lombard • Bân-lâm-gú (Min Nan) • ဘာသာမန် (Mon) • Nynorsk (Norwegian) • Occitan • Oromoo (Oromo) • پښتو (Pashto) • ਪੰਜਾਬੀ (Punjabi) • Српски (Serbian) • လိၵ်ႈတႆ (Shan) • Sicilianu (Sicilian) • Simple English • Slovenčina (Slovak) • Kiswahili (Swahili) • Tagalog • Тоҷикӣ (Tajik) • Українська (Ukrainian) • اردو (Urdu) • Volapük • Walon (Walloon) • Cymraeg (Welsh)"
a4 = "Armãneashce (Aromanian) • Aymara • Беларуская (Belarusian) • Bosanski (Bosnian) • Bikol • Corsu (Corsican) • Føroyskt (Faroese) • Fiji Hindi • Kalaallisut (Greenlandic) • Avañe'ẽ (Guaraní) • Interlingua • Interlingue • Gaeilge (Irish) • كٲشُر (Kashmiri) • Kaszëbsczi (Kashubian) • қазақша (Kazakh) • ភាសាខ្មែរ (Khmer) • Кыргызча (Kyrgyz) • Lëtzebuergesch (Luxembourgish) • Māori • Plattdüütsch (Low Saxon) • Македонски (Macedonian) • Malti (Maltese) • मराठी (Marathi) • Nahuatl • नेपाली (Nepali) • Li Niha (Nias) • Ænglisc (Old English) • Gàidhlig (Scottish Gaelic) • Tacawit (Shawiya) • سنڌي (Sindhi) • සිංහල (Sinhalese) • Slovenščina (Slovene) • Soomaaliga (Somali) • Hornjoserbsce (Upper Sorbian) • seSotho (Southern Sotho) • Basa Sunda (Sundanese) • Tatarça / Татарча (Tatar) • تركمن / Туркмен (Turkmen) • Uyghurche / ئۇيغۇرچە (Uyghur) • پنجابی (Western Punjabi) • Wollof (Wolof) • isiZulu (Zulu)"
a5 = "አማርኛ (Amharic) • Aragonés (Aragonese) • ᏣᎳᎩ (Cherokee) • Kernewek / Karnuack (Cornish) • ދިވެހިބަސް (Divehi) • ગુજરાતી (Gujarati) • Hausa / هَوُسَ (Hausa) • ʻŌlelo Hawaiʻi (Hawaiian) • ᐃᓄᒃᑎᑐᑦ (Inuktitut) • Ikinyarwanda (Kinyarwanda) • Lingala • Gaelg (Manx) • Монгол (Mongolian) • Runa Simi (Quechua) • Gagana Samoa (Samoan) • Sängö • Setswana • ትግርኛ (Tigrinya) • Tok Pisin • Xitsonga (Tsonga) • ייִדיש (Yiddish)"

