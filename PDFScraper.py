# Import the required packages
import tabula as tb
import pandas as pd
import pdfquery

df = tb.read_pdf('C:\\Users\\john.cox\\GitHub\\TimberBids\\KL-341-2021-GF9818-01 Exhibit A.pdf', pages='all')
print(df)

pdf = pdfquery.PDFQuery('C:\\Users\\john.cox\\GitHub\\TimberBids\\KL-341-2021-GF9818-01 Exhibit A.pdf')
pdf.load()

pdf.tree.write('pdfXMLtest',pretty_print=True)

pdf.extract([('text',':contains("EXHIBIT")')])