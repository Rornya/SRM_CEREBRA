from django.shortcuts import render, get_object_or_404, redirect
from .models import Chat, Message

def chat_list(request):
    chats = request.user.chats.all()
    return render(request, 'chats/chat_list.html', {'chats': chats})

def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
            return redirect('chat_detail', chat_id=chat.id)
    return render(request, 'chats/chat_detail.html', {'chat': chat})

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    chat_messages = ticket.chat_messages.all()
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.ticket = ticket
            chat_message.user = request.user
            chat_message.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = ChatMessageForm()

    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'form': form, 'chat_messages': chat_messages})