django-akuna-components
=======================

Django Detail, Create, Update and Delete component based views. They extend the generic Django Class Based Views preserving the existing functionality but adding hooks for component like forms and factories.  

ComponentCreateView
-------------------

    from akcomponent.views import ComponentCreateView

    class MyCreateView(ComponentCreateView):
        # could add generic django Create CBV stuff here 
        pass

  
As with standard django class based views, use as_view() to initialise the view, passing in the ContentType instance of the object being created.

    view_func = MyCreateView.as_view(content_type=<content type obj>, **kwargs)
    return view_func(request)

(Instead of ContentType instance, could pass content_type_name='<app label>.<lower case model name>' to the as_view func.)

### Forms

To customise MyCreateView, create and register a 'FormClass' component:

    from django import forms

    class CustomerForm(forms.Form):
        first_name = forms.CharField()
        surname    = forms.CharField()

    from akuna.component import register_component 

    # register component for the customer content type name (<app label>.<lowercase model name>)  
    register_component(CustomerForm, is_a='FormClass', name='myapp.customer')


Now any time MyCreateView.as_view is called passing in the Customer content type, CustomerForm class will be used.  If MyCreateView is called with a content type other than Customer, processing will fall back as per standard django create view.  Or could create a generic form catching other content types:

    class GenericForm(forms.Form):
        # some generic form stuff here
        pass

    # register form without the name
    register_component(GenericForm, is_a='FormClass')


Now MyCreateView will use the GenericForm for all content types other than 'myapp.customer'.


### Create Factories

ComponentCreateView also contains a hook for content creation factories. So similar to forms above, could register factory components per content type. 

'CreateFactory' for content of 'myapp.customer' type:

    def customer_create_factory(request, content_type, **form_cleaned_data):
        # create customer instance here
        pass

    register_component(customer_create_factory, is_a='CreateFactory', name='myapp.customer')


Could fall back to standard generic django Create CBV processing to create content objects other than 'myapp.customer' type. Or could create a generic factory to catch other content types.

    def generic_create_factory(request, content_type, **form_cleaned_data):
        # something like -
        model_class = content_type.model_class()
        content_object = model_class(**form_cleaned_data)
        content_object.save()

    register_component(generic_create_factory, is_a='CreateFactory')

If no 'CreateFactory' defined, will fall back to django CBV generic CreateView form_valid() and content object creation.


ComponentUpdateView
-------------------

### Update Factories

Similar to Create Factories above, except update factory recieves content object (being updated) as one of the arguments.

Example Update Factory for objects of 'myapp.customer' content type:

    def customer_update_factory(request, customer_object, **form_cleaned_data):
        # update customer object here
        pass

    register_component(customer_update_factory, is_a='UpdateFactory', name='myapp.customer')


Generic Update Factory for all other content types:

    def generic_update_factory(request, content_object, **form_cleaned_data):
        # generic content_object update processing here
        pass

    register_component(generic_update_factory, is_a='UpdateFactory')


If no 'UpdateFactory' defined, will fall back to django CBV generic UpdateView form_valid() and content update.
        

ComponentDeleteView
-------------------

### Delete Factories

Similar to Update Factories above, delete factory will receive content object being deleted as on of the arguments.

Example Delete Factory for objects of 'myapp.customer' content type:

    def customer_delete_factory(request, customer_object, **form_cleaned_data):
        # customer object delete processing here
        pass

    register_component(customer_delete_factory, is_a='DeleteFactory', name='myapp.customer')


Generic Delete Factory for all other content types:

    def generic_delete_factory(request, content_object, **form_cleaned_data):
        # some generic object delete processing
        pass

    register_component(generic_delete_factory, is_a='DeleteFactory')
 

If no 'DeleteFactory' defined, will fall back to django CBV DeleteView delete().

