# -*- encoding: utf-8 -*-
from google.appengine.ext import ndb
from google.appengine.ext.blobstore import BlobInfo

class DuplicatedContainerName(Exception):
    pass

class Container(ndb.Model):
    name = ndb.StringProperty(required = True)
    help = ndb.StringProperty(required = True, indexed = False)
    order = ndb.IntegerProperty(required = True, indexed = False)
    container = ndb.KeyProperty(kind = 'Container')

    def _pre_put_hook(self):
        if not self.key.id():
            if Container.query(Container.name == self.name).count() > 0:
                raise DuplicatedContainerName('name already exists')

    def get_containerkey(self, name):
        thecontainer = ndb.gql("SELECT __key__ FROM Container WHERE name = :1", name).get()
        return thecontainer

class DuplicatedItemName(Exception):
    pass

class Item(ndb.Model):
    name = ndb.StringProperty(required = True, indexed = False)
    help = ndb.StringProperty(required = True, indexed = False)
    route = ndb.StringProperty(required = True)
    order = ndb.IntegerProperty(required = True, indexed = False)
    container = ndb.KeyProperty(kind = Container)

    def _pre_put_hook(self):
        if not self.key.id():
            if Item.query(Item.route == self.route).count() > 0:
                raise DuplicatedItemName('route already exists')

    def get_item_route(self, route):
        theitem = ndb.gql("SELECT * FROM Item WHERE route = :1", route).get()
        return theitem

    def get_nav(self):
        nav = []
        items = ndb.gql("SELECT * FROM Item").fetch()
        for i in items:
            navitem = []
            grade = 0
            navitem.append([int(i.key.id()), int(i.container.id()), True, i.name, i.help, i.route, i.order, grade])
            # Read the leaf container
            grade += 1
            leafcontainer = ndb.gql("SELECT * FROM Container WHERE __key__ = :1", i.container).get()
            father_id = leafcontainer.container
            if father_id:
                father_id = int(leafcontainer.container.id())
            navitem.append([int(leafcontainer.key.id()), father_id, False, leafcontainer.name, leafcontainer.help, None, leafcontainer.order, grade])
            father = leafcontainer.container
            while father:
                grade += 1
                fathercontainer = ndb.gql("SELECT * FROM Container WHERE __key__ = :1", father).get()
                father_id = fathercontainer.container
                if father_id:
                    father_id = int(fathercontainer.container.id())
                navitem.append([int(fathercontainer.key.id()), father_id, False, fathercontainer.name, fathercontainer.help, None, fathercontainer.order, grade])
                father = fathercontainer.container
            maxlevel = len(navitem)
            level = maxlevel
            for j in range(0, maxlevel):
                navitem[j].append(level - 1)
                level -= 1
            # Identify the first container already in nav and store its grade
            grade = 0
            isinnav = False
            for ni in navitem:
                if grade > 0:
                    for n in nav:
                        if ni[0] == n[0]:
                            isinnav = True
                if isinnav:
                    break
                grade += 1
            # Erase containers already in nav according to its grade
            while True:
                if navitem[-1][7] >= grade:
                    navitem.pop()
                else:
                    break
            while len(navitem):
                nav.append(navitem.pop())
        return nav

class DuplicatedIngredientName(Exception):
    pass

class Ingredient(ndb.Model):
    name = ndb.StringProperty(required = True)

    def _pre_put_hook(self):
        if not self.key.id():
            if Ingredient.query(Ingredient.name == self.name).count() > 0:
                raise DuplicatedIngredientName('name already exists')

    def get_ingredientkey(self, name):
        theingredient = ndb.gql("SELECT __key__ FROM Ingredient WHERE name = :1", name).get()
        return theingredient

class DuplicatedSpecialityName(Exception):
    pass

class Speciality(ndb.Model):
    name = ndb.StringProperty(required = True)

    def _pre_put_hook(self):
        if not self.key.id():
            if Speciality.query(Speciality.name == self.name).count() > 0:
                raise DuplicatedSpecialityName('name already exists')

    def get_specialitykey(self, name):
        thespeciality = ndb.gql("SELECT __key__ FROM Speciality WHERE name = :1", name).get()
        return thespeciality

    def get_specialities(self):
        specialities = ndb.gql("SELECT * FROM Speciality").order(Speciality.name).fetch()
        s = []
        s.append((0, 'Select an speciality'))
        for speciality in specialities:
            s.append((speciality.key.id(), speciality.name))
        return s

class DuplicatedDishName(Exception):
    pass

class Dish(ndb.Model):
    name = ndb.StringProperty(required = True)
    description = ndb.StringProperty(required = True, indexed = False)
    servings = ndb.IntegerProperty(required = True, indexed = False)
    directions = ndb.StringProperty(required = True, indexed = False)
    photo = ndb.BlobKeyProperty()
    video = ndb.BlobKeyProperty()
    audio = ndb.BlobKeyProperty()
    photogallery = ndb.BlobKeyProperty(repeated=True)
    speciality = ndb.KeyProperty(kind = Speciality)

    def _pre_put_hook(self):
        if not self.key.id():
            if Dish.query(Dish.name == self.name).count() > 0:
                raise DuplicatedDishName('name already exists')

    def get_dishkey(self, name):
        thedish = ndb.gql("SELECT __key__ FROM Dish WHERE name = :1", name).get()
        return thedish

    def get_dishes(self, speciality_id):
        thespeciality = ndb.Key('Speciality', speciality_id)
        dishes = ndb.gql("SELECT * FROM Dish WHERE speciality = :1", thespeciality).order(Dish.name).fetch()
        d = []
        d.append((0, 'Select a dish'))
        for dish in dishes:
            d.append((dish.key.id(), dish.name))
        return d

    def getphoto(self, dish_id):
        dish = Dish.get_by_id(int(dish_id))
        docinfo = BlobInfo.get(dish.photo)
        return docinfo

    def getaudio(self, dish_id):
        dish = Dish.get_by_id(int(dish_id))
        docinfo = BlobInfo.get(dish.audio)
        return docinfo

    def getvideo(self, dish_id):
        dish = Dish.get_by_id(int(dish_id))
        docinfo = BlobInfo.get(dish.video)
        return docinfo

    def getphotogallery(self, dish_id):
        dish = Dish.get_by_id(int(dish_id))
        docinfo = BlobInfo.get(dish.photogallery)
        return docinfo

    def update(self, dish_id, description, servings, directions):
        dish = Dish.get_by_id(int(dish_id))
        actualizar = False
        if dish.description != description:
            dish.description = description
            actualizar = True
        if dish.servings != servings:
            dish.servings = servings
            actualizar = True
        if dish.directions != directions:
            dish.directions = directions
            actualizar = True
        if actualizar:
            dish.put()

    def updatephoto(self, dish_id, photo):
        dish = Dish.get_by_id(int(dish_id))
        if dish.photo:
            blob_info = BlobInfo.get(dish.photo)
            blob_info.delete()
        dish.photo = photo
        dish.put()

    def updateaudio(self, dish_id, audio):
        dish = Dish.get_by_id(int(dish_id))
        if dish.audio:
            blob_info = BlobInfo.get(dish.audio)
            blob_info.delete()
        dish.audio = audio
        dish.put()

    def updatevideo(self, dish_id, video):
        dish = Dish.get_by_id(int(dish_id))
        if dish.video:
            blob_info = BlobInfo.get(dish.video)
            blob_info.delete()
        dish.video = video
        dish.put()

    def updatephotogallery(self, dish_id, photogallery):
        dish = Dish.get_by_id(int(dish_id))
        for photo in dish.photogallery:
            blob_info = BlobInfo.get(photo)
            blob_info.delete()
        dish.photogallery = []
        for photo in photogallery:
            dish.photogallery.append(photo)
        dish.put()

class DuplicatedUnitName(Exception):
    pass

class Unit(ndb.Model):
    name = ndb.StringProperty(required = True)

    def _pre_put_hook(self):
        if not self.key.id():
            if Unit.query(Unit.name == self.name).count() > 0:
                raise DuplicatedUnitName('name already exists')

    def get_unitkey(self, name):
        theunit = ndb.gql("SELECT __key__ FROM Unit WHERE name = :1", name).get()
        return theunit

class DuplicatedIngredientdish(Exception):
    pass

class Ingredientdish(ndb.Model):
    quantity = ndb.FloatProperty(required = True, indexed = False)
    unit = ndb.KeyProperty(kind = Unit)
    dish = ndb.KeyProperty(kind = Dish)
    ingredient = ndb.KeyProperty(kind = Ingredient)
    order = ndb.IntegerProperty(required = True)

    def _pre_put_hook(self):
        if not self.key.id():
            if Unit.query(Ingredientdish.unit == self.unit and Ingredientdish.dish == self.dish and Ingredientdish.ingredient == self.ingredient).count() > 0:
                raise DuplicatedIngredientdish('Ingredient Dish already exists')

    def get_ingredientsofadish(self, dish_id):
        thedish = ndb.Key('Dish', dish_id)
        ing = ndb.gql("SELECT * FROM Ingredientdish WHERE dish = :1", thedish).order(Ingredientdish.order).fetch()
        ingredients = []
        for i in ing:
            ingredient = i.ingredient.get()
            unit = i.unit.get()
            ingredients.append([ingredient.name, i.quantity, unit.name])
        return ingredients
