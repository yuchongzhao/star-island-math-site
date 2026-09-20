import unittest,server,time,base64,io
from PIL import Image
class GenerationTests(unittest.TestCase):
 def setUp(self): server.CONFIG.update(provider='fake-test-only',signing='unit-test-signing-not-deployed')
 def pages(self): return [{'image':1,'page':12,'lesson':'宿建德江','text':'移舟泊烟渚，日暮客愁新。野旷天低树，江清月近人。','assignment':''}]
 def cards(self): return {'verified':True,'cards':[{'image':1,'kind':'word','text':'野旷','pinyin':'yě kuàng','clue':'野旷是田野开阔','tip':''},{'image':1,'kind':'recite','text':'野旷天低树，江清月近人。','pinyin':'','clue':'远野与江月','tip':''}]}
 def test_exact_source_check_rejects_invented_words(self):
  x=self.cards();x['cards'][0]['text']='花朵'
  with self.assertRaises(server.Problem):server.validate_cards(x,self.pages(),'both','src-test')
 def test_unverified_and_partial_pages_rejected(self):
  with self.assertRaises(server.Problem):server.validate_pages({'readable':True,'pages':self.pages()},2)
  x=self.cards();x['verified']=False
  with self.assertRaises(server.Problem):server.validate_cards(x,self.pages(),'both','src-test')
 def test_duplicate_cards_and_answer_leak(self):
  x=self.cards();x['cards'].append(x['cards'][0].copy());out=server.validate_cards(x,self.pages(),'both','src-test');self.assertEqual(len(out),2);self.assertNotIn('野旷',out[0]['clue'])
 def test_scope_must_supply_requested_task_types(self):
  x=self.cards();x['cards']=x['cards'][:1]
  with self.assertRaises(server.Problem):server.validate_cards(x,self.pages(),'both','src-test')
 def test_tokens_expiry_tampering_purpose(self):
  token=server.mint('device','unit-device',60);self.assertEqual(server.check_token(token,'device'),'unit-device')
  for t,kind in [(token+'a','device'),(token,'activate'),(server.mint('device','x',-1),'device')]:
   with self.assertRaises(server.Problem):server.check_token(t,kind)
 def test_images_validated_and_metadata_stripped(self):
  b=io.BytesIO();Image.new('RGB',(500,500),'white').save(b,'PNG');uri='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode();ims,mode=server.prepare_images({'images':[uri]});self.assertTrue(ims[0].startswith('data:image/jpeg;'));self.assertEqual(mode,'both')
  for images in [[],[uri]*5,['https://example.com/secret'],['data:image/png;base64,invalid']]:
   with self.assertRaises(server.Problem):server.prepare_images({'images':images})
 def test_headings_never_become_recitation_and_overlaps_are_skipped(self):
  p=self.pages();p[0]['text']='宿建德江\n[唐]孟浩然\n'+p[0]['text'];p[0]['author']='孟浩然'
  pages=server.validate_pages({'readable':True,'pages':p},1)
  self.assertNotIn('孟浩然',pages[0]['text']);self.assertNotIn('宿建德江',pages[0]['text'])
  x=self.cards();x['cards'] += [{'image':1,'kind':'word','text':'宿建德江','pinyin':'sù jiàn dé jiāng'},{'image':1,'kind':'recite','text':'江清月近人。','clue':''}]
  out=server.validate_cards(x,pages,'both','test');self.assertEqual(len(out),2)
 def test_quota_separates_days_and_limits_device(self):
  server.COUNTS.clear()
  for i in range(12):server.prune_and_quota('test-device')
  with self.assertRaises(server.Problem):server.prune_and_quota('test-device')
if __name__=='__main__':unittest.main()
