from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter

class VotersListView(ListView):
    '''View to display list of voters with filters'''
    
    template_name = 'voter_analytics/voters.html'
    model = Voter
    context_object_name = 'voters'
    paginate_by = 100
    
    def get_queryset(self):
        '''Filter voters based on form parameters'''
        
        voters = super().get_queryset().order_by('last_name', 'first_name')
        
        # party affiliation
        if 'party_affiliation' in self.request.GET:
            party = self.request.GET['party_affiliation']
            if party:
                voters = voters.filter(party_affiliation=party)
        
        # minimum birth year
        if 'min_birth_year' in self.request.GET:
            min_year = self.request.GET['min_birth_year']
            if min_year:
                voters = voters.filter(date_of_birth__year__gte=min_year)
        
        # maximum birth year
        if 'max_birth_year' in self.request.GET:
            max_year = self.request.GET['max_birth_year']
            if max_year:
                voters = voters.filter(date_of_birth__year__lte=max_year)
        
        # voter score
        if 'voter_score' in self.request.GET:
            score = self.request.GET['voter_score']
            if score:
                voters = voters.filter(voter_score=score)
        
        # s pecific elections
        if 'v20state' in self.request.GET:
            voters = voters.filter(v20state=True)
        
        if 'v21town' in self.request.GET:
            voters = voters.filter(v21town=True)
        
        if 'v21primary' in self.request.GET:
            voters = voters.filter(v21primary=True)
        
        if 'v22general' in self.request.GET:
            voters = voters.filter(v22general=True)
        
        if 'v23town' in self.request.GET:
            voters = voters.filter(v23town=True)
        
        return voters


class VoterDetailView(DetailView):
    '''View to show detail page for one voter'''
    
    template_name = 'voter_analytics/voter_detail.html'
    model = Voter
    context_object_name = 'voter'