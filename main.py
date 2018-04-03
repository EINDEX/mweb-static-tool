import datetime
import copy
from sqlalchemy import create_engine

from models import Tag, Cat, Article, CatArticle, TagArticle
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass, field

engine = create_engine('sqlite:///mainlib.db')
Session = sessionmaker(bind=engine)

# 缓存
cats = {}
tags = {}
md_list = []


def init():
    global cats, tags
    session = Session()
    tags = {tag.tid: tag for tag in session.query(Tag)}
    cats = {cat.uuid: cat for cat in session.query(Cat)}


@dataclass
class HexoSource:
    layout: str = 'page'
    title: str = ''
    date: int = 0
    updated: int = 0
    permalink: str = ''
    content: str = ''
    comments: bool = True
    tags: list = field(default_factory=list)
    categories: list = field(default_factory=list)

    def format(self):
        output = ''
        output += f'title: {self.title}\n'
        output += f'date: {datetime.datetime.fromtimestamp(self.date).strftime("%Y/%m/%d %H:%M:%S")}\n'
        output += f'updated: {datetime.datetime.fromtimestamp(self.updated).strftime("%Y/%m/%d %H:%M:%S")}\n'
        output += f'permalink: {self.permalink}\n'
        output += f'layout: {self.layout}\n'
        output += f'comments: {self.comments}\n'
        output += f'tags: \n'
        for t in self.tags:
            output += f'- {t}\n'
        output += f'categories: \n'
        for c in self.categories:
            output += f'- {c}\n'
        output += f'---\n'
        output += self.content
        return output


def gene_all_hexo_source_by_name(name):
    global md_list
    session = Session()
    main_cat = session.query(Cat).filter_by(name=name).first()

    def get_all_article_by_id(uuid, cat_list):
        if not cat_list:
            cat_list = []
        for cat in session.query(Cat).filter_by(uuid=uuid):
            for ca in session.query(CatArticle).filter_by(rid=cat.uuid):
                a = session.query(Article).filter_by(uuid=ca.aid, state=1).first()
                if isinstance(a, Article):
                    source = HexoSource()
                    source.layout = 'page' if a.a_type else 'post'
                    source.date = a.dateAdd
                    source.updated = a.dateModif
                    source.permalink = a.docName if a.docName else a.uuid
                    source.tags = [tags[t.rid].name for t in session.query(TagArticle).filter_by(aid=a.uuid)]
                    source.categories = cat_list
                    with open(f'docs/{a.uuid}.md', 'r') as f:
                        start = True
                        for line in f.readlines():
                            if line.startswith('# ') and start:
                                start = False
                                source.title = line.replace('# ', '').strip()
                            elif not start:
                                source.content += line
                    print(source)
                    md_list.append(source)
        for sub_cat in session.query(Cat).filter_by(pid=uuid):
            c_list = copy.copy(cat_list)
            c_list.append(sub_cat.name)
            get_all_article_by_id(sub_cat.uuid, c_list)

    get_all_article_by_id(main_cat.uuid, [])


def gene_new_markdowns(md_list):
    for md in md_list:
        if md.layout == 'post':
            with open(f'hexo/source/_posts/{md.permalink}.md', 'w') as f:
                f.write(md.format())
        elif md.layout == 'page':
            with open(f'hexo/source/{md.permalink}.md', 'w') as f:
                f.write(md.format())


if __name__ == '__main__':
    init()
    gene_all_hexo_source_by_name('eindex.me')
    gene_new_markdowns(md_list)
