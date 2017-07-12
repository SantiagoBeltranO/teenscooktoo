# -*- encoding: utf-8 -*-
import os
import jinja2
import webapp2
from models.models import *
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from libs import mylib

template_dir = os.path.join(os.path.dirname(__file__), 'views')
jinja_env = jinja2.Environment (loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True,
                                extensions = ['jinja2.ext.autoescape'])

class Handler(webapp2.RequestHandler):

    def initialize(self, request, response):
        super(Handler, self).initialize(request, response)
        request.is_ajax = lambda:request.environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Index(Handler):

    def get(self):
        cadenanav = mylib.getcadenanav()
        self.render("index.html", cadenanav = cadenanav, is_ajax = self.request.is_ajax())

class Home(Handler):

    def get(self):
        is_ajax = self.request.is_ajax()
        cadenanav = ""
        if not is_ajax:
            cadenanav = mylib.getcadenanav()
        self.render("intro.html", cadenanav = cadenanav, is_ajax = is_ajax)

class About(Handler):

    def get(self):
        is_ajax = self.request.is_ajax()
        cadenanav = ""
        if not is_ajax:
            cadenanav = mylib.getcadenanav()
        self.render("about.html", cadenanav = cadenanav, is_ajax = is_ajax)

class Details(Handler):

    def get(self):
        is_ajax = self.request.is_ajax()
        cadenanav = ""
        if not is_ajax:
            cadenanav = mylib.getcadenanav()
        self.render("details.html", cadenanav = cadenanav, is_ajax = is_ajax)

class Tools(Handler):

    def get(self):
        is_ajax = self.request.is_ajax()
        cadenanav = ""
        if not is_ajax:
            cadenanav = mylib.getcadenanav()
        self.render("tools.html", cadenanav = cadenanav, is_ajax = is_ajax)

class Health(Handler):

    def get(self):
        is_ajax = self.request.is_ajax()
        cadenanav = ""
        if not is_ajax:
            cadenanav = mylib.getcadenanav()
        self.render("health.html", cadenanav = cadenanav, is_ajax = is_ajax)


class Consult(Handler):

    def get(self):
        speciality = Speciality()
        specialities = speciality.get_specialities()
        option = 'consult'
        self.render("selspeciality.html", specialities = specialities,
                                          option=option)

    def post(self):
        dish_id = self.request.get('dish_id', default_value=None)
        thedish = Dish.get_by_id(int(dish_id))
        thedish.description = mylib.formatcadena(thedish.description)
        thedish.directions = mylib.formatcadena(thedish.directions)
        photo = ""
        if thedish.photo:
            photo = str(thedish.photo)
        audio = ""
        if thedish.audio:
            audio = str(thedish.audio)
        video = ""
        if thedish.video:
            video = str(thedish.video)
        photogallery = ""
        if thedish.photogallery:
            photogallery = str(thedish.photogallery)
        ingredientdish = Ingredientdish()
        ingredients = ingredientdish.get_ingredientsofadish(int(dish_id))
        for ingredient in ingredients:
            ingredient[2] = mylib.formatunidad(ingredient[2])
            ingredient[1] = mylib.formatquantity(ingredient[1])

        self.render("consultadish.html", thedish = thedish,
                                         ingredients = ingredients,
                                         photo = photo,
                                         audio = audio,
                                         video = video,
                                         photogallery = photogallery)

class Recap(Handler):
    def get(self):
        speciality = Speciality()
        specialities = speciality.get_specialities()
        option = 'recap'
        self.render("selspeciality.html", specialities = specialities,
                                          option=option)

class Update(Handler):

    def get(self):
        self.render("restricted.html")

    def post(self):
        restricted = self.request.get('restricted', default_value=None)
        if restricted:
            if restricted == "e44165d04caec1113db6159d0210c4c3":
                speciality = Speciality()
                specialities = speciality.get_specialities()
                option = 'update'
                self.render("selspeciality.html", specialities = specialities,
                                                  option=option)
            else:
                self.render("intro.html")
        else:
            dish_id = self.request.get('dish_id', default_value=None)
            description = self.request.get('description', default_value=None)
            servings = self.request.get('servings', default_value=None)
            directions = self.request.get('directions', default_value=None)
            if description:
                dish = Dish()
                dish.update(dish_id, description, int(servings), directions)
            else:
                upload_url_photo = blobstore.create_upload_url('/photos/' + dish_id)
                upload_url_audio = blobstore.create_upload_url('/audios/' + dish_id)
                upload_url_video = blobstore.create_upload_url('/videos/' + dish_id)
                upload_url_photogallery = blobstore.create_upload_url('/photogallery/' + dish_id)
                thedish = Dish.get_by_id(int(dish_id))
                self.render("updateadish.html", thedish = thedish,
                                                dish_id = int(dish_id),
                                                upload_url_photo = upload_url_photo,
                                                upload_url_audio = upload_url_audio,
                                                upload_url_video = upload_url_video,
                                                upload_url_photogallery = upload_url_photogallery)

class Dishesspeciality(Handler):

    def post(self, option):
        speciality_id = self.request.get('speciality_id', default_value=None)
        if option == 'recap':
            thespeciality = ndb.Key('Speciality', int(speciality_id))
            dishes = ndb.gql("SELECT * FROM Dish WHERE speciality = :1", thespeciality).order(Dish.name).fetch()
            i = 0
            for d in dishes:
                dishes[i].description = mylib.formatcadena(d.description)
                i += 1
            self.render("recapspeciality.html", dishes=dishes)
        else:
            dish = Dish()
            dishes = dish.get_dishes(int(speciality_id))
            self.render("dishesspeciality.html", dishes=dishes,
                                                 option=option)

class Photos(Handler, blobstore_handlers.BlobstoreUploadHandler, blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, dish_id):
        dish = Dish()
        infophoto = dish.getphoto(dish_id)
        self.send_blob(infophoto, save_as=True)

    def post(self, dish_id):
        upload_files = self.get_uploads('photo')
        if len(upload_files) == 0:
            photo = None
        else:
            blob_info = upload_files[0]
            photo = blob_info.key()
            """
            Actualizar photo
            """
            dish = Dish()
            dish.updatephoto(dish_id, photo)
        self.response.headers['Content-Type'] = 'text/plain'
        self.redirect('/')

class Audios(Handler, blobstore_handlers.BlobstoreUploadHandler, blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, dish_id):
        dish = Dish()
        infoaudio = dish.getaudio(dish_id)
        self.send_blob(infoaudio, save_as=True)

    def post(self, dish_id):
        upload_files = self.get_uploads('audio')
        if len(upload_files) == 0:
            audio = None
        else:
            blob_info = upload_files[0]
            audio = blob_info.key()
            """
            Actualizar audio
            """
            dish = Dish()
            dish.updateaudio(dish_id, audio)
        self.response.headers['Content-Type'] = 'text/plain'
        self.redirect('/')

class Videos(Handler, blobstore_handlers.BlobstoreUploadHandler, blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, dish_id):
        dish = Dish()
        infovideo = dish.getvideo(dish_id)
        self.send_blob(infovideo, save_as=True)

    def post(self, dish_id):
        upload_files = self.get_uploads('video')
        if len(upload_files) == 0:
            audio = None
        else:
            blob_info = upload_files[0]
            video = blob_info.key()
            """
            Actualizar video
            """
            dish = Dish()
            dish.updatevideo(dish_id, video)
        self.response.headers['Content-Type'] = 'text/plain'
        self.redirect('/')

class Photogallery(Handler, blobstore_handlers.BlobstoreUploadHandler, blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, dish_id):
        dish = Dish()
        infophotogallery = dish.getphotogallery(dish_id)
        self.send_blob(infophotogallery, save_as=True)

    def post(self, dish_id):
        upload_files = self.get_uploads('photogallery')
        if len(upload_files) == 0:
            photogallery = None
        else:
            photogallery = []
            for blob_info in upload_files:
                photogallery.append(blob_info.key())
            """
            Actualizar photos de la galería
            """
            dish = Dish()
            dish.updatephotogallery(dish_id, photogallery)
        self.response.headers['Content-Type'] = 'text/plain'
        self.redirect('/')

class GetImage(Handler):

    def get(self):
        id = self.request.get('id')
        photo_info = blobstore.BlobInfo.get(id)
        img = photo_info.open().read()
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(img)

class GetSound(Handler):

    def get(self):
        id = self.request.get('id')
        audio_info = blobstore.BlobInfo.get(id)
        aud = audio_info.open().read()
        self.response.headers['Content-Type'] = 'audio/mp4'
        self.response.out.write(aud)

class GetVideo(Handler):

    def get(self):
        id = self.request.get('id')
        video_info = blobstore.BlobInfo.get(id)
        vid = video_info.open().read()
        self.response.headers['Content-Type'] = 'video/mov'
        self.response.out.write(vid)

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/home', Home),
    ('/about', About),
    ('/details', Details),
    ('/tools', Tools),
    ('/health', Health),
    ('/consult', Consult),
    ('/recap', Recap),
    ('/update', Update),
    ('/dishesspeciality/(\w+)', Dishesspeciality),
    ('/photos/(\d+)', Photos),
    ('/audios/(\d+)', Audios),
    ('/videos/(\d+)', Videos),
    ('/photogallery/(\d+)', Photogallery),
    ('/image', GetImage),
    ('/sound', GetSound),
    ('/video', GetVideo),
], debug=True)