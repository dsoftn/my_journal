import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QStyle,
                             QSlider, QFrame, QSizePolicy, QSpacerItem, QMainWindow)
from PyQt5.QtCore import QRect
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl

import html_parser_cls


html = """
<table class="file-information">
<caption>
Информације о датотеци
</caption>
<tbody>
<tr>
<th scope="row" id="fileinfotpl_desc">
Опис
</th>
<td>
<p>
Антропоморфна фигурина, глина, Вихча - Бело брдо 5500-4500. год. п.н.е. (Народни музеј, Београд) фото: Михаило Грбић
</p>
</td>
</tr>
<tr>
<th scope="row">
Извор
</th>
<td>
Није наведен 
<b>
извор
</b>
. Молимо Вас да додате информације које недостају.
</td>
</tr>
<tr>
<th scope="row">
Датум
</th>
<td>
</td>
</tr>
<tr>
<th scope="row">
Аутор
</th>
<td>
<style data-mw-deduplicate="TemplateStyles:r25172099">
.mw-parser-output .imbox{margin:4px 0;border-collapse:collapse;border:3px solid #36c;background-color:#fbfbfb;box-sizing:border-box}.mw-parser-output .imbox .mbox-text .imbox{margin:0 -0.5em;display:block}.mw-parser-output .imbox-speedy{border:3px solid #b32424;background-color:#fee7e6}.mw-parser-output .imbox-delete{border:3px solid #b32424}.mw-parser-output .imbox-content{border:3px solid #f28500}.mw-parser-output .imbox-style{border:3px solid #fc3}.mw-parser-output .imbox-move{border:3px solid #9932cc}.mw-parser-output .imbox-protection{border:3px solid #a2a9b1}.mw-parser-output .imbox-license{border:3px solid #88a;background-color:#f7f8ff}.mw-parser-output .imbox-featured{border:3px solid #cba135}.mw-parser-output .imbox .mbox-text{border:none;padding:0.25em 0.9em;width:100%}.mw-parser-output .imbox .mbox-image{border:none;padding:2px 0 2px 0.9em;text-align:center}.mw-parser-output .imbox .mbox-imageright{border:none;padding:2px 0.9em 2px 0;text-align:center}.mw-parser-output .imbox .mbox-empty-cell{border:none;padding:0;width:1px}.mw-parser-output .imbox .mbox-invalid-type{text-align:center}@media(min-width:720px){.mw-parser-output .imbox{margin:4px 10%}}
</style>
<table class="plainlinks imbox imbox-style" role="presentation">
<tbody>
<tr>
<td class="mbox-image">
<span typeof="mw:File">
<span>
<img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Edit-clear.svg/40px-Edit-clear.svg.png" decoding="async" width="40" height="40" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Edit-clear.svg/60px-Edit-clear.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Edit-clear.svg/80px-Edit-clear.svg.png 2x" data-file-width="48" data-file-height="48" />
</span>
</span>
</td>
<td class="mbox-text">
Ова датотека нема 
<b>
информације о аутору
</b>
и можда недостају друге информације. 
<br />
Датотеке треба да имају преглед како би се други информисали о садржају, аутору, извору и датуму ако је могуће. Ако знате или имате приступ таквим информацијама, додајте их на страницу датотеке.
<hr />
<small>
Обавијестити отпремаоца са: {{subst:add-desc-I|1=Antropomorfna figurina vinca.jpg}}
</small>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
<tr>
<th scope="row" id="fileinfotpl_perm">
Дозвола
<br />
<small>
(
<a href="https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia" class="extiw" title="commons:Commons:Reusing content outside Wikimedia">
Поновно коришћење ове датотеке
</a>
)
</small>
</th>
<td>
<table style="margin:0.5em auto; width:90%; background-color:#f0f0f0; border:2px solid #aaaaaa; padding:2px;">
<tbody>
<tr>
<td>
<div class="center" style="width:auto; margin-left:auto; margin-right:auto;">
<i>
<b>
Ja, носилац ауторских права над овим делом,
</b>
овим га објављујем под следећим лиценцама:
</i>
</div>
<div class="center" style="width:auto; margin-left:auto; margin-right:auto;">
<i>
<link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r25172099">
<table class="plainlinks imbox imbox-license licensetpl" role="presentation">
<tbody>
<tr>
<td class="mbox-image">
<span typeof="mw:File">
<a href="/wiki/%D0%94%D0%B0%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D0%B0:Heckert_GNU_white.svg" class="mw-file-description" title="GFDL">
<img alt="GFDL" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/22/Heckert_GNU_white.svg/52px-Heckert_GNU_white.svg.png" decoding="async" width="52" height="51" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/22/Heckert_GNU_white.svg/78px-Heckert_GNU_white.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/22/Heckert_GNU_white.svg/104px-Heckert_GNU_white.svg.png 2x" data-file-width="535" data-file-height="523" />
</a>
</span>
</td>
<td class="mbox-text">
Дата је дозвола да се копира, дистрибуира и/или мења овај документ под условима 
<b>
<a href="/wiki/%D0%93%D0%9D%D0%A3-%D0%BE%D0%B2%D0%B0_%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0_%D0%B7%D0%B0_%D1%81%D0%BB%D0%BE%D0%B1%D0%BE%D0%B4%D0%BD%D1%83_%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%98%D1%83" title="ГНУ-ова лиценца за слободну документацију">
ГНУ-ове лиценце за слободну документацију
</a>
</b>
, верзије 1.2 или било које новије верзије коју објави 
<a href="/wiki/%D0%97%D0%B0%D0%B4%D1%83%D0%B6%D0%B1%D0%B8%D0%BD%D0%B0_%D0%B7%D0%B0_%D1%81%D0%BB%D0%BE%D0%B1%D0%BE%D0%B4%D0%BD%D0%B8_%D1%81%D0%BE%D1%84%D1%82%D0%B2%D0%B5%D1%80" title="Задужбина за слободни софтвер">
Задужбина за слободни софтвер
</a>
; без непроменљивих одељака и без текста на насловној и задњој страни. Текст лиценце можете прочитати 
<a href="/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0:GNU_Free_Documentation_License" class="mw-redirect" title="Википедија:GNU Free Documentation License">
овде
</a>
. Подлеже и 
<a href="/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0:%D0%9E%D0%B4%D1%80%D0%B8%D1%86%D0%B0%D1%9A%D0%B5_%D0%BE%D0%B4%D0%B3%D0%BE%D0%B2%D0%BE%D1%80%D0%BD%D0%BE%D1%81%D1%82%D0%B8" title="Википедија:Одрицање одговорности">
општем одрицању
</a>
.
<div style="display: none">
<p>
<span class="licensetpl_short">
GFDL with disclaimers
</span>
<span class="licensetpl_long">
GNU Free Documentation License with 
<a href="/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0:General_disclaimer" class="mw-redirect" title="Википедија:General disclaimer">
disclaimers
</a>
</span>
<span class="licensetpl_link">
//sr.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%98%D0%B0:Text_of_the_GNU_Free_Documentation_License
</span>
</p>
</div>
</td>
</tr>
</tbody>
</table>

<link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r25172099">
<table class="plainlinks imbox imbox-license licensetpl" role="presentation">
<tbody>
<tr>
<td class="mbox-image">
<span class="nowrap">
<span typeof="mw:File">
<a href="/wiki/%D0%94%D0%B0%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D0%B0:CC_some_rights_reserved.svg" class="mw-file-description" title="CC">
<img alt="CC" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/CC_some_rights_reserved.svg/90px-CC_some_rights_reserved.svg.png" decoding="async" width="90" height="36" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/CC_some_rights_reserved.svg/135px-CC_some_rights_reserved.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/79/CC_some_rights_reserved.svg/180px-CC_some_rights_reserved.svg.png 2x" data-file-width="744" data-file-height="300" />
</a>
</span>
<br />
<span typeof="mw:File">
<a href="/wiki/%D0%94%D0%B0%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D0%B0:Cc-by_new_white.svg" class="mw-file-description" title="BY">
<img alt="BY" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Cc-by_new_white.svg/24px-Cc-by_new_white.svg.png" decoding="async" width="24" height="24" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Cc-by_new_white.svg/36px-Cc-by_new_white.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/11/Cc-by_new_white.svg/48px-Cc-by_new_white.svg.png 2x" data-file-width="64" data-file-height="64" />
</a>
</span>
<span typeof="mw:File">
<a href="/wiki/%D0%94%D0%B0%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D0%B0:Cc-by_white.svg" class="mw-file-description" title="&#160;BY">
<img alt="&#160;BY" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Cc-by_white.svg/24px-Cc-by_white.svg.png" decoding="async" width="24" height="24" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Cc-by_white.svg/36px-Cc-by_white.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Cc-by_white.svg/48px-Cc-by_white.svg.png 2x" data-file-width="64" data-file-height="64" />
</a>
</span>
</span>
</td>
<td class="mbox-text">
<i>
Овај рад је лиценциран под условима 
<a href="/wiki/%D0%9A%D1%80%D0%B8%D1%98%D0%B5%D1%98%D1%82%D0%B8%D0%B2_%D0%BA%D0%BE%D0%BC%D0%BE%D0%BD%D1%81" class="mw-redirect" title="Кријејтив комонс">
Кријејтив комонс
</a>

<a rel="nofollow" class="external text" href="http://creativecommons.org/licenses/by/3.0/rs/">
Ауторство 3.0 Србија
</a>
.
<br />
Укратко: можете слободно умножавати, дистрибуирати, јавно саопштавати и прерађивати дело, под условом да на одговарајући начин наведете аутора.
</i>
<div style="display: none">
<p>
<span class="licensetpl_short">
CC-BY-3.0-RS
</span>
<span class="licensetpl_long">
Кријејтив комонс Ауторство 3.0 Србија
</span>
<span class="licensetpl_link">
http://creativecommons.org/licenses/by/3.0/rs/
</span>
</p>
</div>

<i>
</i>
</td>
<td class="mbox-imageright">
<span class="mw-image-border" typeof="mw:File">
<a href="/wiki/%D0%94%D0%B0%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D0%B0:Flag_of_Serbia.svg" class="mw-file-description">
<img src="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/55px-Flag_of_Serbia.svg.png" decoding="async" width="55" height="37" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/83px-Flag_of_Serbia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/110px-Flag_of_Serbia.svg.png 2x" data-file-width="1350" data-file-height="900" />
</a>
</span>
</td>
</tr>
</tbody>
</table>

</i>
</div>
<div class="center" style="width:auto; margin-left:auto; margin-right:auto;">
<span lang="sr" title="српски текст">
Можете да одаберете лиценцу по свом избору.
</span>
<i>
</i>
</div>
</td>
</tr>
</tbody>
</table>
<p>
<br />
</p>
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

        self.show()





app = QApplication([])

proba = Proba(html)
app.exec_()
 


