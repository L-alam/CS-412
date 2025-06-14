from .models import Profile, StatusMessage, Image, StatusImage, Friend
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm, UpdateStatusMessageForm
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

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
    
    def get_context_data(self, **kwargs):
        """Add user authentication context"""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                user_profile = self.request.user.profile_set.first()
                context['is_owner'] = (user_profile == self.object)
            except:
                context['is_owner'] = False
        else:
            context['is_owner'] = False
        return context


class CreateProfileView(CreateView):
    '''Create a new Profile and save it to the db.'''
    
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"
    
    def get_context_data(self, **kwargs):
        """Add the user creation form to the context"""
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        """Process both the UserCreationForm and CreateProfileForm"""
        user_form = UserCreationForm(self.request.POST)
        
        if user_form.is_valid():
            user = user_form.save()
            
            login(self.request, user)
            
            form.instance.user = user
            
            return super().form_valid(form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form)
            )


class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    '''Create a new StatusMessage and save it to the db.'''
    
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        '''Return the dict of context variables'''
        
        context = super().get_context_data(**kwargs)
        
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        if profile.user != self.request.user:
            return redirect('show_profile', pk=pk)
        
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''Handle the form submission and process image uploads.'''
        
        print(f"CreateStatusMessageView.form_valid: form.cleaned_data={form.cleaned_data}")
        
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        if profile.user != self.request.user:
            return redirect('show_profile', pk=pk)
        
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


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''A view to update a Profile and save it to the database.'''
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"
    context_object_name = 'profile'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only update their own profile"""
        profile = self.get_object()
        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)
        return super().dispatch(request, *args, **kwargs)


class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    '''A view to update a StatusMessage and save it to the database.'''
    
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = "mini_fb/update_status_form.html"
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only update their own status messages"""
        status_message = self.get_object()
        if status_message.profile.user != request.user:
            return redirect('show_profile', pk=status_message.profile.pk)
        return super().dispatch(request, *args, **kwargs)



class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    '''A view to delete a StatusMessage and remove it from the database.'''
    
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only delete their own status messages"""
        status_message = self.get_object()
        if status_message.profile.user != request.user:
            return redirect('show_profile', pk=status_message.profile.pk)
        return super().dispatch(request, *args, **kwargs)


class AddFriendView(LoginRequiredMixin, View):
    '''A view to add a friend relationship between two profiles.'''
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        '''Handle the add friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = get_object_or_404(Profile, pk=pk)
        
        if profile.user != request.user:
            return redirect('show_profile', pk=pk)
            
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        profile.add_friend(other_profile)
        
        return redirect('show_profile', pk=pk)


class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    '''Show friend suggestions for a profile.'''
    
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only view friend suggestions for their own profile"""
        profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)
        return super().dispatch(request, *args, **kwargs)


class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    '''Show the news feed for a profile.'''
    
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only view news feed for their own profile"""
        profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)
        return super().dispatch(request, *args, **kwargs)