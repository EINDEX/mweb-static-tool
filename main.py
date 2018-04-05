import datetime
import copy
from pathlib import Path

import fire
from sqlalchemy import create_engine

from models import Tag, Cat, Article, CatArticle, TagArticle
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass, field


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


class MwebSiteHelper:

    def __init__(self, site_name, hexo_src, mweb_src):
        self.site_name = site_name
        self.hexo_src = Path(hexo_src)
        self.mweb_src = Path(mweb_src)
        print(f'sqlite:///{self.mweb_src.expanduser()}/mainlib.db')
        engine = create_engine(f'sqlite:///{self.mweb_src.expanduser()}/mainlib.db')
        self.Session = sessionmaker(bind=engine)

        self.cats = {}
        self.tags = {}
        self.md_list = []

        self.init()
        self.gene_all_hexo_source_by_name(site_name)
        self.write()

    def init(self):
        session = self.Session()
        self.tags = {tag.tid: tag for tag in session.query(Tag)}
        self.cats = {cat.uuid: cat for cat in session.query(Cat)}

    def get_all_article_by_id(self, uuid, cat_list):
        session = self.Session()
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
                    source.tags = [self.tags[t.rid].name for t in session.query(TagArticle).filter_by(aid=a.uuid)]
                    source.categories = cat_list
                    with open(f'{self.mweb_src}/docs/{a.uuid}.md', 'r') as f:
                        start = True
                        for line in f.readlines():
                            if line.startswith('# ') and start:
                                start = False
                                source.title = line.replace('# ', '').strip()
                            elif not start:
                                source.content += line
                    self.md_list.append(source)
        for sub_cat in session.query(Cat).filter_by(pid=uuid):
            c_list = copy.copy(cat_list)
            c_list.append(sub_cat.name)
            self.get_all_article_by_id(sub_cat.uuid, c_list)

    def gene_all_hexo_source_by_name(self, name):
        session = self.Session()
        main_cat = session.query(Cat).filter_by(name=name).first()

        self.get_all_article_by_id(main_cat.uuid, [])

    def write(self):
        for md in self.md_list:

            if md.layout == 'post':
                with open(f'{self.hexo_src}/source/_posts/{md.permalink}.md', 'w') as f:
                    f.write(md.format())
            elif md.layout == 'page':
                with open(f'{self.hexo_src}/source/{md.permalink}.md', 'w') as f:
                    f.write(md.format())
            print(f'Write {md.title}')

        print('Done!')


if __name__ == '__main__':
    fire.Fire(MwebSiteHelper)
