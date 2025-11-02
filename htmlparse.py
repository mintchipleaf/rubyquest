from bs4 import BeautifulSoup
from bs4 import NavigableString
from pathlib import Path


# Input HTML File Path
inputpath = "input\\input.html"
# Output Files` Path
outputpath = "_panels\\{}.md"

with open(inputpath) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

nl = "\n"
fulltabs = "            "
textopen = "text: |-" + nl + fulltabs
commopen = "command: |-" + nl + fulltabs

maxpost = 858
postcount = 0
weaverpostcount = 0
for text in soup.find_all('tr'):
    output = ""
    quotes = []
    commands = []
    texts = []

    postcount += 1
    posttitle = str(postcount).rjust(3, '0')

    # ---
    output += "---{}layout: panel{}".format(nl, nl)

    imgsrc = text.find('img').get('src').rsplit('/', 1)[-1]
    imgsrc = Path(imgsrc).stem

    weaverpost = 'ruby' in imgsrc or 'sruby' in imgsrc or 'icon' in imgsrc

    output += "image: {}{}".format(imgsrc, nl)

    if not weaverpost:
        if postcount != 1:
            output += "prevpost: \"{}\"{}".format(str(postcount - 1).rjust(3, '0'), nl)
        if postcount != maxpost:
            output += "nextpost: \"{}\"{}".format(str(postcount + 1).rjust(3, '0'), nl)

    def separatecomms(block):
        lines = []
        i = 0
        linenumber = 0
        taginline = 1
        lineinentry = 1

        def addtext(text, first):
            nonlocal taginline
            nonlocal linenumber
            nonlocal lineinentry

            prefix = "- "

            if taginline == 1:
                if len(lines) > 0:
                    lines[linenumber - 1] += nl
                if lineinentry > 1:
                    prefix = "  "
                lines.append("  {}{}".format(prefix, first))
                linenumber += 1
            lines[linenumber - 1] += str(text)
        #end addtext

        def parsetag(tag):
            nonlocal taginline
            nonlocal lineinentry

            # Strip <br> tags coming before or after text block
            if tag.name == 'br':
                if taginline > 1 and tag.next_sibling:
                    if isinstance(tag.next_sibling, NavigableString) or tag.next_sibling.name == 'span' or tag.next_sibling.name == 'a':
                        addtext(nl + fulltabs , textopen)
                    else:
                        addtext(nl, textopen)
                return

            # Text tag
            if isinstance(tag, NavigableString):
                addtext(str(tag), textopen)
                taginline += 1
            # Non-string tag
            elif tag.name=='font':
                    taginline = 1
                    lineinentry = 1
                    texttouse = tag.contents

                    if tag.string:
                        texttouse = tag.string.replace(">", "")

                    addtext(texttouse, commopen)
                    lineinentry += 1
            # Special
            else:
                addtext(str(tag), textopen)
                taginline += 1
        #end parsetag

        for tag in block.children:
            i += 1
            parsetag(tag)

        return lines
    #end separatecomms

    # Quote
    allquotes = text.find_all('div', 'someone-elses-post')
    for quoteblock in allquotes:
        for quote in quoteblock.find_all('p'):
            quotes.append(separatecomms(quote))

        quoteblock.decompose()

    if len(quotes) > 0:
        output += "quotes:{}".format(nl)
        for quote in quotes:
            for qline in quote:
                output += qline
            output += nl

    # Command
    spantext = text.find('span', 'text')
    lines = separatecomms(spantext)
    if len(lines) > 0:
        output += "lines:{}".format(nl)
        for line in lines:
            output += line
        output += nl

    # ---
    output += "---"

    # Weaver post
    if weaverpost:
        weaverpostcount += 1
        posttitle += "-" + str(weaverpostcount)
        postcount -= 1
    else:
        weaverpostcount = 0

    filename = str(posttitle)
    with open(outputpath.format(filename), "w") as file:
        file.seek(0)
        file.write(str(output))
        file.truncate()
print(postcount)