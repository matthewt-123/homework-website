@login_required(login_url='/login')
def addhw1(request):
    class AddHwForm(ModelForm):
        forms.DateInput.input_type="date"
        class Meta:
            model = Homework
            fields = ['hw_class', 'hw_title', 'due_date', 'priority', 'notes']
        def __init__(self, *args, **kwargs):
            super(AddHwForm, self).__init__(*args, **kwargs)
            self.fields['hw_class'].queryset = Class.objects.filter(class_user=request.user)
    if request.method == 'POST':
        form = AddHwForm(request.POST)
        if form.is_valid():
            #append new hw to database
            hw_class = form.cleaned_data['hw_class']
            hw_title = form.cleaned_data['hw_title']
            due_date = form.cleaned_data['due_date']
            priority = form.cleaned_data['priority']
            notes = form.cleaned_data['notes']
            addhw = Homework(hw_user=request.user, hw_class=hw_class, hw_title=hw_title, priority=priority, notes=notes, due_date=due_date, completed=False)
            addhw.save()

            time = Class.objects.get(class_user = request.user, class_name =hw_class).time
            time = datetime.combine(due_date, time)

            #check to see if user has calendar, create event: 
            calendar = CalendarEvent.objects.get(calendar_user = request.user)
            e = Event()
            e.name = hw_title
            e.begin = time
            e.description = notes
            try:
                c = Calendar(calendar.ics)
            except:
                c = Calendar()
            c.events.add(e) 

            #append new hw to database
            calendar.ics = c
            calendar.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'hwapp/addhw.html', {
                'form': form,
            })
    else:

        form = AddHwForm()
        return render(request, 'hwapp/addhw.html', {
            'form': form
        })