from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.forms.models import modelform_factory
from django.db.models import Model 
from django.http import HttpResponseRedirect

from akuna.component import query_component

import logging
logger = logging.getLogger('akcomponent')


class ComponentDetailView(DetailView):

    content_object = None 

    def get_object(self):
        return self.content_object


class ComponentCreateView(CreateView):

    content_type  = None
    content_type_name = None
    form_class = None

    def get_form_class(self):
        if not self.form_class:
            if self.content_type_name:
                # content type specific form class hook
                self.__class__.form_class = query_component('FormClass', name=self.content_type_name)
            if not self.form_class:
                # generic form class 
                self.__class__.form_class = query_component('FormClass')
            if not self.form_class:
                model_cls = self.content_type.model_class()
                if issubclass(model_cls, Model):
                    self.__class__.form_class = modelform_factory(model_cls)

        return super(ComponentCreateView, self).get_form_class()

    def form_valid(self, form):
        logger.debug('Form class: %s, ct name: "%s"' % (self.form_class, content_type_name))

        create_factory = None
        if self.content_type_name:
            # content type specific create factory hook 
            create_factory = query_component('CreateFactory', name=self.content_type_name)
        if not create_factory:
            # try generic create factory
            create_factory = query_component('CreateFactory')

        if create_factory:
            logger.debug('Create factory: %s' % str(create_factory))
            create_factory(self.request, self.content_type, **form.cleaned_data)
            return HttpResponseRedirect(self.get_success_url())

        logger.debug('No create factory, defaulting to CreateView form_valid')

        return super(ComponentCreateView, self).form_valid(form)


class ComponentUpdateView(UpdateView): 

    content_object = None
    content_type_name = None
    form_class = None

    def get_object(self):
        return self.content_object

    def get_content_type_name(self):
        if self.content_type_name:
            return self.content_type_name
        if isinstance(self.content_object, Model):
            return self.content_object._meta.app_label + '.' + self.content_object._meta.object_name.lower()
        return None 

    def get_form_class(self):
        if not self.form_class:
            content_type_name = self.get_content_type_name() 
            if content_type_name:
                # content type specific form class hook
                self.__class__.form_class = query_component('FormClass', name=content_type_name)
            if not self.form_class:
                # generic form class 
                self.__class__.form_class = query_component('FormClass')
            if not self.form_class:
                if isinstance(self.content_object, Model):
                    self.__class__.form_class = modelform_factory(self.content_object.__class__)

        return super(ComponentUpdateView, self).get_form_class()

    def form_valid(self, form):
        content_type_name = self.get_content_type_name() 

        logger.debug('Form class: %s, ct name: "%s"' % (self.form_class, content_type_name))

        update_factory = None
        if content_type_name:
            # content type specific update factory hook 
            update_factory = query_component('UpdateFactory', name=content_type_name)
        if not update_factory:
            # try generic update factory
            update_factory = query_component('UpdateFactory')

        if update_factory:
            logger.debug('Update factory: %s' % str(update_factory))
            update_factory(self.request, self.content_object, **form.cleaned_data)
            return HttpResponseRedirect(self.get_success_url())

        logger.debug('No update factory, defaulting to UpdateView form_valid')

        # default Django UpdateView update 
        return super(ComponentUpdateView, self).form_valid(form)


class ComponentDeleteView(DeleteView):

    content_object = None
    content_type_name = None

    def get_object(self):
        return self.content_object

    def get_content_type_name(self):
        if self.content_type_name:
            return self.content_type_name
        if isinstance(self.content_object, Model):
            return self.content_object._meta.app_label + '.' + self.content_object._meta.object_name.lower()
        return None 

    def delete(self, request, *args, **kwargs):
        content_type_name = self.get_content_type_name()

        logger.debug('ct name: "%s"' % content_type_name)

        delete_factory = None
        if content_type_name:
            delete_factory = query_component('DeleteFactory', name=content_type_name)
            if not delete_factory:
                delete_factory = query_component('DeleteFactory')

        if delete_factory:
            logger.debug('Delete factory: %s' % str(delete_factory))
            delete_factory(request, self.content_object, **kwargs)
            return HttpResponseRedirect(self.get_success_url())

        logger.debug('No delete factory, defaulting to DeleteView delete')

        return super(ComponentDeleteView, self).delete(request, *args, **kwargs)
