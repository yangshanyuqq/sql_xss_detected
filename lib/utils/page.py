#-*-coding:utf-8-*-
import lxml.html.soupparser as soupparser
import requests
headers = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
}
def lcs(a, b):
    lena=len(a)
    lenb=len(b)
    c=[[0 for i in range(lenb+1)] for j in range(lena+1)]
    for i in range(lena):
        for j in range(lenb):
            if a[i]==b[j]:
                c[i+1][j+1]=c[i][j]+1
            elif c[i+1][j]>c[i][j+1]:
                c[i+1][j+1]=c[i+1][j]
            else:
                c[i+1][j+1]=c[i][j+1]
    return c[lena][lenb]

def get_domtree(html):
    dom = soupparser.fromstring(html)
    for child in dom.iter():
        yield child.tag

def similar_web(html1, html2):
    dom_tree1 = ">".join(list(filter(lambda e: isinstance(e,str),list(get_domtree(html1)))))
    dom_tree2 = ">".join(list(filter(lambda e: isinstance(e,str),list(get_domtree(html2)))))
    # print(lcs(dom_tree1,dom_tree2))
    length = lcs(dom_tree1,dom_tree2)
    return 2.0*length/(len(dom_tree1)+len(dom_tree2))
    # return 0

'''a_url = 'http://192.168.45.1/sqli-labs-master/Less-1/?id=1\'and\'1\'=\'1'
b_url = 'http://192.168.45.1/sqli-labs-master/Less-1/index.php?id=1%27'
html1 = requests.get(a_url,headers=headers).text
html2 = requests.get(b_url,headers=headers).text
percent = similar_web(html1, html2)
print(percent) #相似度（百分比）'''