"""Build WidgetCraft's public catalogue from category folders. Python standard library only."""
from pathlib import Path
import argparse,base64,hashlib,json,re,struct

def catalogue(root):
    entries=[];ids=set();category_order={};preferred=['Brutalist','Minimalist','Editorial','Bauhaus','Retro Pixel','Art Deco','Soft Pastel','Studio originals']
    for path in sorted(root.rglob('*.widget.json')):
        relative=path.relative_to(root).as_posix()
        if any(part.startswith('.') for part in path.relative_to(root).parts):continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]{0,179}',relative):raise ValueError('Use simple category and template filenames: '+relative)
        raw=path.read_bytes()
        if len(raw)>4*1024*1024:raise ValueError('Template exceeds4MiB: '+relative)
        doc=json.loads(raw);name=doc.get('name','').strip()
        if doc.get('format')!='widget-maker' or not 1<=doc.get('schemaVersion',0)<=5:raise ValueError('Unsupported widget document: '+relative)
        if not name or len(name)>80 or '\n' in name:raise ValueError('Invalid widget name: '+relative)
        if not 48<=doc.get('width',0)<=800 or not 48<=doc.get('height',0)<=800 or not 0<=len(doc.get('layers',[]))<=40:raise ValueError('Invalid canvas or layer count: '+relative)
        for key,value in doc.get('assets',{}).items():
            if not re.fullmatch('[a-f0-9]{64}',key) or hashlib.sha256(base64.b64decode(value,validate=True)).hexdigest()!=key:raise ValueError('Asset hash does not match: '+relative)
        group=path.relative_to(root).parts[0] if len(path.relative_to(root).parts)>1 else 'studio-originals'
        category_file=root/group/'category.json';settings=json.loads(category_file.read_text()) if category_file.exists() else {}
        style=settings.get('name',group.replace('-',' ').title());style='Studio originals' if style=='Studio Originals' else style
        if not isinstance(style,str) or not style.strip() or len(style)>40 or '\n' in style:raise ValueError('Invalid category name: '+group)
        style=style.strip();category_order[style]=int(settings.get('order',preferred.index(style) if style in preferred else 100))
        stem=path.name.removesuffix('.widget.json');identifier=re.sub('[^a-z0-9-]+','-',relative.removesuffix('.widget.json').lower().replace('/','-')).strip('-')
        if not identifier or len(identifier)>120 or identifier in ids:raise ValueError('Template IDs must be unique: '+relative)
        ids.add(identifier)
        layer_text=json.dumps(doc.get('layers',[])).lower();aliases=[]
        if 'media.' in layer_text or 'media_' in layer_text:aliases.append('music audio media')
        if 'fitness.' in layer_text:aliases.append('fitness activity health')
        if 'weather.' in layer_text:aliases.append('weather forecast')
        if 'calendar.' in layer_text:aliases.append('calendar agenda appointment')
        if 'api.' in layer_text:aliases.append('web api connection')
        keywords=(' '.join(aliases)+' '+stem.replace('-',' ')+' '+' '.join(sorted(set(layer.get('type','text') for layer in doc.get('layers',[]))))).strip()[:180]
        item=dict(id=identifier,name=name,style=style,keywords=keywords,width=doc['width'],height=doc['height'],layers=len(doc['layers']),document=relative,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        preview=path.with_name(stem+'.png')
        if preview.exists():
            image=preview.read_bytes()
            if len(image)>2*1024*1024 or image[:8]!=b'\x89PNG\r\n\x1a\n' or len(image)<24:raise ValueError('Use a PNG preview under2MiB: '+relative)
            w,h=struct.unpack('>II',image[16:24])
            if not 1<=w<=2048 or not 1<=h<=2048 or w*h>3_000_000:raise ValueError('Preview dimensions exceed budget: '+relative)
            item['preview']=dict(file=preview.relative_to(root).as_posix(),bytes=len(image),sha256=hashlib.sha256(image).hexdigest(),imageWidth=w,imageHeight=h,x=0,y=0,width=w,height=h)
        entries.append(item)
    if not 1<=len(entries)<=500:raise ValueError('Catalogue supports1..500 templates')
    styles=sorted(category_order,key=lambda key:(category_order[key],key.lower()))
    if len(styles)>60:raise ValueError('Catalogue supports at most60 categories')
    entries.sort(key=lambda item:(styles.index(item['style']),item['name'].lower(),item['id']))
    revision=hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
    result=json.dumps(dict(schemaVersion=1,revision=revision,styles=styles,templates=entries),ensure_ascii=False,indent=2)+'\n'
    if len(result.encode())>512*1024:raise ValueError('Catalogue metadata exceeds512KiB')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'));parser.add_argument('--output',type=Path,default=Path('catalog.json'));args=parser.parse_args()
    result=catalogue(args.root.resolve());args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(result,encoding='utf-8')
    data=json.loads(result);print(f"Catalogue:{len(data['templates'])}templates,{len(data['styles'])}categories,revision{data['revision']}")
