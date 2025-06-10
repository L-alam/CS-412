from .models import Profile, StatusMessage, Image, StatusImage, Friend
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm, UpdateStatusMessageForm
from django.urls import reverse
import random

# Create your views here.
class ShowAllProfilesView(ListView):
    """Show all Profiles on one page"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    """Show one Profile on the page"""
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    '''Create a new Profile and save it to the db.'''
    
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"


class CreateStatusMessageView(CreateView):
    '''Create a new StatusMessage and save it to the db.'''
    
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs):
        '''Return the dict of context variables'''
        
        context = super().get_context_data(**kwargs)
        
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''Handle the form submission and process image uploads.'''
        
        print(f"CreateStatusMessageView.form_valid: form.cleaned_data={form.cleaned_data}")
        
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        form.instance.profile = profile
        sm = form.save()
        
        files = self.request.FILES.getlist('files')
        print(f"CreateStatusMessageView: files={files}")
        
        for file in files:
            image = Image(
                profile=profile,
                image_file=file
            )
            image.save()
            
            status_image = StatusImage(
                status_message=sm,
                image=image
            )
            status_image.save()
        
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''
        
        pk = self.kwargs['pk']
        return reverse('show_profile', kwargs={'pk': pk})


class UpdateProfileView(UpdateView):
    '''A view to update a Profile and save it to the database.'''
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"
    context_object_name = 'profile'


class UpdateStatusMessageView(UpdateView):
    '''A view to update a StatusMessage and save it to the database.'''
    
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = "mini_fb/update_status_form.html"
    
    def get_success_url(self):
        '''Return the URL to redirect to after successful update.'''
        status_message = self.get_object()
        return reverse('show_profile', kwargs={'pk': status_message.profile.pk})


class DeleteStatusMessageView(DeleteView):
    '''A view to delete a StatusMessage and remove it from the database.'''
    
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'
    
    def get_success_url(self):
        '''Return the URL to which we should be directed after the delete.'''
        status_message = self.get_object()
        profile = status_message.profile
        
        return reverse('show_profile', kwargs={'pk': profile.pk})


class AddFriendView(View):
    '''A view to add a friend relationship between two profiles.'''
    
    def dispatch(self, request, *args, **kwargs):
        '''Handle the add friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = Profile.objects.get(pk=pk)
        other_profile = Profile.objects.get(pk=other_pk)
        
        profile.add_friend(other_profile)
        
        return redirect('show_profile', pk=pk)


class ShowFriendSuggestionsView(DetailView):
    '''Show friend suggestions for a profile.'''
    
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'


class ShowNewsFeedView(DetailView):
    '''Show the news feed for a profile.'''
    
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'