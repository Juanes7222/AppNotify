import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getEvents, createEvent, updateEvent, deleteEvent, getContacts, addSubscription, removeSubscription, getEventSubscriptions } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Calendar } from '../components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger, SheetFooter } from '../components/ui/sheet';
import { Checkbox } from '../components/ui/checkbox';
import { 
  Plus, 
  Calendar as CalendarIcon, 
  Clock, 
  MapPin, 
  Users, 
  Trash2, 
  Edit, 
  MoreVertical,
  Loader2,
  Search,
  X
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../components/ui/dropdown-menu';
import { motion, AnimatePresence } from 'framer-motion';
import { format, parseISO, isPast } from 'date-fns';
import { es } from 'date-fns/locale';
import { toast } from 'sonner';
import { cn } from '../lib/utils';

const REMINDER_UNITS = [
  { value: 'minutes', label: 'Minutos' },
  { value: 'hours', label: 'Horas' },
  { value: 'days', label: 'Días' },
  { value: 'weeks', label: 'Semanas' },
  { value: 'custom', label: 'Personalizado' },
];

const EventCard = ({ event, onEdit, onDelete }) => {
  const eventDate = parseISO(event.event_date);
  const isEventPast = isPast(eventDate);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      layout
    >
      <Card className={cn(
        "hover:border-primary/50 transition-all duration-300 group",
        isEventPast && "opacity-60"
      )}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-lg group-hover:text-primary transition-colors">
                <Link to={`/events/${event.id}`} data-testid={`event-link-${event.id}`}>
                  {event.title}
                </Link>
              </CardTitle>
              <CardDescription className="flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1">
                  <CalendarIcon className="w-3 h-3" />
                  {format(eventDate, "dd MMM yyyy", { locale: es })}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {format(eventDate, "HH:mm")}
                </span>
              </CardDescription>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8" data-testid={`event-menu-${event.id}`}>
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onEdit(event)} data-testid={`edit-event-${event.id}`}>
                  <Edit className="w-4 h-4 mr-2" />
                  Editar
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => onDelete(event.id)} 
                  className="text-destructive"
                  data-testid={`delete-event-${event.id}`}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Eliminar
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {event.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {event.description}
            </p>
          )}
          
          {event.location && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="w-4 h-4" />
              <span>{event.location}</span>
            </div>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-border">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">{event.subscribers_count || 0} suscriptores</span>
            </div>
            
            {event.reminder_intervals?.length > 0 && (
              <Badge variant="secondary" className="text-xs">
                {event.reminder_intervals.length} recordatorios
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const EventForm = ({ event, onSubmit, onClose, loading, contacts, existingSubscriptions }) => {
  const [formData, setFormData] = useState({
    title: event?.title || '',
    description: event?.description || '',
    event_date: event?.event_date ? parseISO(event.event_date) : new Date(),
    location: event?.location || '',
    reminder_intervals: event?.reminder_intervals || [],
    selectedContacts: existingSubscriptions || [], // Contactos ya suscritos o nuevos
  });
  const [time, setTime] = useState(
    event?.event_date 
      ? format(parseISO(event.event_date), 'HH:mm')
      : '12:00'
  );
  const [contactSearch, setContactSearch] = useState('');

  const handleAddReminder = () => {
    setFormData(prev => ({
      ...prev,
      reminder_intervals: [...prev.reminder_intervals, { value: 1, unit: 'days', custom_date: null }]
    }));
  };

  const handleRemoveReminder = (index) => {
    setFormData(prev => ({
      ...prev,
      reminder_intervals: prev.reminder_intervals.filter((_, i) => i !== index)
    }));
  };

  const handleReminderChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      reminder_intervals: prev.reminder_intervals.map((r, i) => {
        if (i !== index) return r;
        
        if (field === 'unit' && value === 'custom') {
          // Al cambiar a personalizado, inicializar con fecha/hora actual
          return { ...r, unit: 'custom', value: null, custom_date: new Date().toISOString() };
        } else if (field === 'unit' && value !== 'custom') {
          // Al cambiar de personalizado a otro, remover custom_date
          return { ...r, unit: value, value: r.value || 1, custom_date: null };
        } else if (field === 'value') {
          return { ...r, value: parseInt(value) || 1 };
        } else if (field === 'custom_date') {
          return { ...r, custom_date: value };
        } else {
          return { ...r, [field]: value };
        }
      })
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Combine date and time
    const [hours, minutes] = time.split(':');
    const eventDateTime = new Date(formData.event_date);
    eventDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

    onSubmit({
      ...formData,
      event_date: eventDateTime.toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">Título del evento *</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Ej: Reunión de equipo"
          required
          data-testid="event-title-input"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Descripción</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Detalles del evento..."
          rows={3}
          data-testid="event-description-input"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Fecha *</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className="w-full justify-start text-left font-normal"
                data-testid="event-date-picker"
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {format(formData.event_date, "dd MMM yyyy", { locale: es })}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={formData.event_date}
                onSelect={(date) => date && setFormData(prev => ({ ...prev, event_date: date }))}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>

        <div className="space-y-2">
          <Label htmlFor="time">Hora *</Label>
          <Input
            id="time"
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            required
            data-testid="event-time-input"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="location">Ubicación</Label>
        <Input
          id="location"
          value={formData.location}
          onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
          placeholder="Ej: Sala de conferencias"
          data-testid="event-location-input"
        />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Recordatorios</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddReminder}
            data-testid="add-reminder-btn"
          >
            <Plus className="w-4 h-4 mr-1" />
            Agregar
          </Button>
        </div>
        
        <div className="space-y-2">
          {formData.reminder_intervals.map((reminder, index) => (
            <div key={index} className="space-y-2 p-3 border rounded-lg bg-muted/50">
              <div className="flex items-center gap-2">
                <Select
                  value={reminder.unit}
                  onValueChange={(value) => handleReminderChange(index, 'unit', value)}
                >
                  <SelectTrigger className="flex-1" data-testid={`reminder-unit-${index}`}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {REMINDER_UNITS.map((unit) => (
                      <SelectItem key={unit.value} value={unit.value}>
                        {unit.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemoveReminder(index)}
                  data-testid={`remove-reminder-${index}`}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              {reminder.unit === 'custom' ? (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Fecha</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-left font-normal text-xs h-9"
                        >
                          <CalendarIcon className="mr-2 h-3 w-3" />
                          {reminder.custom_date ? format(parseISO(reminder.custom_date), 'dd MMM yyyy', { locale: es }) : 'Seleccionar'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={reminder.custom_date ? parseISO(reminder.custom_date) : new Date()}
                          onSelect={(date) => {
                            if (date) {
                              const currentTime = reminder.custom_date ? parseISO(reminder.custom_date) : new Date();
                              date.setHours(currentTime.getHours(), currentTime.getMinutes());
                              handleReminderChange(index, 'custom_date', date.toISOString());
                            }
                          }}
                          locale={es}
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div>
                    <Label className="text-xs">Hora</Label>
                    <Input
                      type="time"
                      className="h-9 text-xs"
                      value={reminder.custom_date ? format(parseISO(reminder.custom_date), 'HH:mm') : '12:00'}
                      onChange={(e) => {
                        const [hours, minutes] = e.target.value.split(':');
                        const customDate = reminder.custom_date ? parseISO(reminder.custom_date) : new Date();
                        customDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
                        handleReminderChange(index, 'custom_date', customDate.toISOString());
                      }}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="1"
                    value={reminder.value || 1}
                    onChange={(e) => handleReminderChange(index, 'value', e.target.value)}
                    className="w-20 h-9"
                    data-testid={`reminder-value-${index}`}
                  />
                  <span className="text-sm text-muted-foreground">
                    {REMINDER_UNITS.find(u => u.value === reminder.unit)?.label.toLowerCase()} antes
                  </span>
                </div>
              )}
            </div>
          ))}
          
          {formData.reminder_intervals.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-2">
              Sin recordatorios configurados
            </p>
          )}
        </div>
      </div>

      {/* Selector de contactos */}
      {contacts && contacts.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Contactos a notificar {event && <span className="text-xs text-muted-foreground">(se agregarán/removerán al guardar)</span>}</Label>
            <Badge variant="secondary">
              {formData.selectedContacts.length} seleccionados
            </Badge>
          </div>
          
          <Input
            placeholder="Buscar contacto..."
            value={contactSearch}
            onChange={(e) => setContactSearch(e.target.value)}
            className="mb-2"
          />
          
          <div className="max-h-48 overflow-y-auto space-y-2 border rounded-md p-3">
            {contacts
              .filter(contact => 
                contact.name.toLowerCase().includes(contactSearch.toLowerCase()) ||
                contact.email.toLowerCase().includes(contactSearch.toLowerCase())
              )
              .map((contact) => (
                <div key={contact.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={`contact-${contact.id}`}
                    checked={formData.selectedContacts.includes(contact.id)}
                    onCheckedChange={(checked) => {
                      setFormData(prev => ({
                        ...prev,
                        selectedContacts: checked
                          ? [...prev.selectedContacts, contact.id]
                          : prev.selectedContacts.filter(id => id !== contact.id)
                      }));
                    }}
                  />
                  <label
                    htmlFor={`contact-${contact.id}`}
                    className="flex-1 text-sm cursor-pointer"
                  >
                    <div className="font-medium">{contact.name}</div>
                    <div className="text-xs text-muted-foreground">{contact.email}</div>
                  </label>
                </div>
              ))}
          </div>
          
          {contacts.filter(contact => 
            contact.name.toLowerCase().includes(contactSearch.toLowerCase()) ||
            contact.email.toLowerCase().includes(contactSearch.toLowerCase())
          ).length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              No se encontraron contactos
            </p>
          )}
        </div>
      )}

      <SheetFooter className="gap-2">
        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading} data-testid="save-event-btn">
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Guardando...
            </>
          ) : (
            event ? 'Actualizar' : 'Crear Evento'
          )}
        </Button>
      </SheetFooter>
    </form>
  );
};

const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [existingSubscriptions, setExistingSubscriptions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchEvents = async () => {
    try {
      const response = await getEvents();
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Error al cargar los eventos');
    } finally {
      setLoading(false);
    }
  };

  const fetchContacts = async () => {
    try {
      const response = await getContacts();
      setContacts(response.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };

  useEffect(() => {
    fetchEvents();
    fetchContacts();
  }, []);

  const handleCreateEvent = async (data) => {
    setFormLoading(true);
    try {
      const { selectedContacts, ...eventData } = data;
      const response = await createEvent(eventData);
      const newEvent = response.data;
      
      // Suscribir los contactos seleccionados
      if (selectedContacts && selectedContacts.length > 0) {
        for (const contactId of selectedContacts) {
          try {
            await addSubscription(newEvent.id, contactId);
          } catch (err) {
            console.error(`Error subscribing contact ${contactId}:`, err);
          }
        }
        toast.success(`Evento creado con ${selectedContacts.length} contacto(s) suscrito(s)`);
      } else {
        toast.success('Evento creado correctamente');
      }
      
      setSheetOpen(false);
      fetchEvents();
    } catch (error) {
      console.error('Error creating event:', error);
      toast.error('Error al crear el evento');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateEvent = async (data) => {
    setFormLoading(true);
    try {
      const { selectedContacts, ...eventData } = data;
      await updateEvent(editingEvent.id, eventData);
      
      // Gestionar suscripciones
      if (selectedContacts) {
        // Obtener suscriptores actuales
        const currentSubsResponse = await getEventSubscriptions(editingEvent.id);
        const currentSubscribers = currentSubsResponse.data.map(sub => sub.contact_id);
        
        // Determinar quién agregar y quién remover
        const toAdd = selectedContacts.filter(id => !currentSubscribers.includes(id));
        const toRemove = currentSubscribers.filter(id => !selectedContacts.includes(id));
        
        // Agregar nuevos suscriptores
        for (const contactId of toAdd) {
          try {
            await addSubscription(editingEvent.id, contactId);
          } catch (err) {
            console.error(`Error subscribing contact ${contactId}:`, err);
          }
        }
        
        // Remover suscriptores
        for (const contactId of toRemove) {
          try {
            const subToRemove = currentSubsResponse.data.find(sub => sub.contact_id === contactId);
            if (subToRemove) {
              await removeSubscription(editingEvent.id, subToRemove.id);
            }
          } catch (err) {
            console.error(`Error removing subscription for contact ${contactId}:`, err);
          }
        }
        
        if (toAdd.length > 0 || toRemove.length > 0) {
          toast.success(`Evento actualizado (${toAdd.length} agregados, ${toRemove.length} removidos)`);
        } else {
          toast.success('Evento actualizado correctamente');
        }
      } else {
        toast.success('Evento actualizado correctamente');
      }
      
      setSheetOpen(false);
      setEditingEvent(null);
      setExistingSubscriptions([]);
      fetchEvents();
    } catch (error) {
      console.error('Error updating event:', error);
      toast.error('Error al actualizar el evento');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!window.confirm('¿Estás seguro de eliminar este evento?')) return;
    
    try {
      await deleteEvent(eventId);
      toast.success('Evento eliminado correctamente');
      fetchEvents();
    } catch (error) {
      console.error('Error deleting event:', error);
      toast.error('Error al eliminar el evento');
    }
  };

  const handleEdit = async (event) => {
    setEditingEvent(event);
    
    // Cargar suscriptores existentes
    try {
      const subsResponse = await getEventSubscriptions(event.id);
      const subscriberIds = subsResponse.data.map(sub => sub.contact_id);
      setExistingSubscriptions(subscriberIds);
    } catch (error) {
      console.error('Error loading subscriptions:', error);
      setExistingSubscriptions([]);
    }
    
    setSheetOpen(true);
  };

  const handleCloseSheet = () => {
    setSheetOpen(false);
    setEditingEvent(null);
    setExistingSubscriptions([]);
  };

  const filteredEvents = events.filter(event =>
    event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="events-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Eventos</h1>
          <p className="text-muted-foreground">
            Gestiona tus eventos y recordatorios
          </p>
        </div>
        
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <SheetTrigger asChild>
            <Button className="glow-primary-hover" data-testid="create-event-btn">
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Evento
            </Button>
          </SheetTrigger>
          <SheetContent className="sm:max-w-lg overflow-y-auto">
            <SheetHeader>
              <SheetTitle>{editingEvent ? 'Editar Evento' : 'Crear Nuevo Evento'}</SheetTitle>
              <SheetDescription>
                {editingEvent 
                  ? 'Modifica los detalles del evento'
                  : 'Completa la información para crear un nuevo evento'
                }
              </SheetDescription>
            </SheetHeader>
            <div className="mt-6">
              <EventForm
                event={editingEvent}
                onSubmit={editingEvent ? handleUpdateEvent : handleCreateEvent}
                onClose={handleCloseSheet}
                loading={formLoading}
                contacts={contacts}
                existingSubscriptions={existingSubscriptions}
              />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar eventos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
          data-testid="search-events-input"
        />
      </div>

      {/* Events Grid */}
      {filteredEvents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filteredEvents.map((event) => (
              <EventCard
                key={event.id}
                event={event}
                onEdit={handleEdit}
                onDelete={handleDeleteEvent}
              />
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <Card className="py-12">
          <CardContent className="flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
              <CalendarIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">
              {searchQuery ? 'No se encontraron eventos' : 'No hay eventos'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery 
                ? 'Intenta con otra búsqueda'
                : 'Crea tu primer evento para comenzar'
              }
            </p>
            {!searchQuery && (
              <Button onClick={() => setSheetOpen(true)} data-testid="empty-create-event-btn">
                <Plus className="w-4 h-4 mr-2" />
                Crear Evento
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EventsPage;
