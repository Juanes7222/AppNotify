import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getEvent, getEventSubscriptions, addSubscription, removeSubscription, getContacts, deleteEvent } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  ArrowLeft, 
  Calendar, 
  Clock, 
  MapPin, 
  Users, 
  Bell, 
  Trash2, 
  Plus,
  Loader2,
  UserPlus,
  Mail
} from 'lucide-react';
import { motion } from 'framer-motion';
import { format, parseISO, differenceInDays, differenceInHours } from 'date-fns';
import { es } from 'date-fns/locale';
import { toast } from 'sonner';

const EventDetailPage = () => {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingSubscription, setAddingSubscription] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState('');

  const fetchData = async () => {
    try {
      const [eventRes, subsRes, contactsRes] = await Promise.all([
        getEvent(eventId),
        getEventSubscriptions(eventId),
        getContacts()
      ]);
      setEvent(eventRes.data);
      setSubscriptions(subsRes.data);
      setContacts(contactsRes.data);
    } catch (error) {
      console.error('Error fetching event data:', error);
      toast.error('Error al cargar los datos del evento');
      navigate('/events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [eventId]);

  const handleAddSubscription = async () => {
    if (!selectedContactId) return;
    
    setAddingSubscription(true);
    try {
      await addSubscription(eventId, selectedContactId);
      toast.success('Contacto suscrito al evento');
      setSelectedContactId('');
      fetchData();
    } catch (error) {
      console.error('Error adding subscription:', error);
      toast.error(error.response?.data?.detail || 'Error al suscribir contacto');
    } finally {
      setAddingSubscription(false);
    }
  };

  const handleRemoveSubscription = async (subscriptionId) => {
    if (!window.confirm('¿Estás seguro de eliminar esta suscripción?')) return;
    
    try {
      await removeSubscription(eventId, subscriptionId);
      toast.success('Suscripción eliminada');
      fetchData();
    } catch (error) {
      console.error('Error removing subscription:', error);
      toast.error('Error al eliminar suscripción');
    }
  };

  const handleDeleteEvent = async () => {
    if (!window.confirm('¿Estás seguro de eliminar este evento? Esta acción no se puede deshacer.')) return;
    
    try {
      await deleteEvent(eventId);
      toast.success('Evento eliminado');
      navigate('/events');
    } catch (error) {
      console.error('Error deleting event:', error);
      toast.error('Error al eliminar el evento');
    }
  };

  const getTimeUntilEvent = () => {
    if (!event) return '';
    const eventDate = parseISO(event.event_date);
    const days = differenceInDays(eventDate, new Date());
    const hours = differenceInHours(eventDate, new Date()) % 24;
    
    if (days < 0) return 'Evento pasado';
    if (days === 0 && hours <= 0) return 'Evento en progreso';
    if (days === 0) return `En ${hours} horas`;
    if (days === 1) return `Mañana`;
    return `En ${days} días`;
  };

  const availableContacts = contacts.filter(
    contact => !subscriptions.some(sub => sub.contact_id === contact.id)
  );

  const getReminderLabel = (interval) => {
    const units = {
      minutes: 'minutos',
      hours: 'horas',
      days: 'días',
      weeks: 'semanas'
    };
    return `${interval.value} ${units[interval.unit]} antes`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!event) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Evento no encontrado</p>
        <Link to="/events">
          <Button variant="link">Volver a eventos</Button>
        </Link>
      </div>
    );
  }

  const eventDate = parseISO(event.event_date);

  return (
    <div className="space-y-6" data-testid="event-detail-page">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/events')} data-testid="back-btn">
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{event.title}</h1>
          <p className="text-muted-foreground">{getTimeUntilEvent()}</p>
        </div>
        <Button variant="destructive" onClick={handleDeleteEvent} data-testid="delete-event-btn">
          <Trash2 className="w-4 h-4 mr-2" />
          Eliminar
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Event Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle>Detalles del Evento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Fecha</p>
                    <p className="font-medium">{format(eventDate, "EEEE, dd MMMM yyyy", { locale: es })}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Clock className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Hora</p>
                    <p className="font-medium font-mono">{format(eventDate, "HH:mm")}</p>
                  </div>
                </div>

                {event.location && (
                  <div className="flex items-start gap-3 sm:col-span-2">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Ubicación</p>
                      <p className="font-medium">{event.location}</p>
                    </div>
                  </div>
                )}
              </div>

              {event.description && (
                <div className="pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground mb-2">Descripción</p>
                  <p className="text-foreground">{event.description}</p>
                </div>
              )}

              {/* Reminders */}
              <div className="pt-4 border-t border-border">
                <div className="flex items-center gap-2 mb-3">
                  <Bell className="w-4 h-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Recordatorios configurados</p>
                </div>
                {event.reminder_intervals?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {event.reminder_intervals.map((interval, index) => (
                      <Badge key={index} variant="secondary">
                        {getReminderLabel(interval)}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Sin recordatorios configurados</p>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Estadísticas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-primary" />
                  <span className="text-sm">Suscriptores</span>
                </div>
                <span className="font-mono font-bold">{subscriptions.length}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-amber-500" />
                  <span className="text-sm">Recordatorios</span>
                </div>
                <span className="font-mono font-bold">{event.reminder_intervals?.length || 0}</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Subscribers */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Suscriptores</CardTitle>
                  <CardDescription>Contactos que recibirán recordatorios</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add subscriber */}
              <div className="flex items-center gap-2">
                <Select value={selectedContactId} onValueChange={setSelectedContactId}>
                  <SelectTrigger className="flex-1" data-testid="select-contact">
                    <SelectValue placeholder="Seleccionar contacto..." />
                  </SelectTrigger>
                  <SelectContent>
                    {availableContacts.length > 0 ? (
                      availableContacts.map((contact) => (
                        <SelectItem key={contact.id} value={contact.id}>
                          {contact.name} ({contact.email})
                        </SelectItem>
                      ))
                    ) : (
                      <div className="px-2 py-4 text-center text-sm text-muted-foreground">
                        {contacts.length === 0 
                          ? 'No hay contactos disponibles' 
                          : 'Todos los contactos ya están suscritos'
                        }
                      </div>
                    )}
                  </SelectContent>
                </Select>
                <Button 
                  onClick={handleAddSubscription} 
                  disabled={!selectedContactId || addingSubscription}
                  data-testid="add-subscriber-btn"
                >
                  {addingSubscription ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4 mr-2" />
                      Agregar
                    </>
                  )}
                </Button>
              </div>

              {contacts.length === 0 && (
                <div className="text-center py-4 border border-dashed border-border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">No tienes contactos creados</p>
                  <Link to="/contacts">
                    <Button variant="outline" size="sm">
                      <Plus className="w-4 h-4 mr-2" />
                      Crear contacto
                    </Button>
                  </Link>
                </div>
              )}

              {/* Subscribers list */}
              {subscriptions.length > 0 ? (
                <div className="space-y-2">
                  {subscriptions.map((sub) => (
                    <div
                      key={sub.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-sm font-medium text-primary">
                            {sub.contact?.name?.charAt(0).toUpperCase() || '?'}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{sub.contact?.name}</p>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {sub.contact?.email}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRemoveSubscription(sub.id)}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        data-testid={`remove-subscriber-${sub.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No hay suscriptores</p>
                  <p className="text-sm">Agrega contactos para enviarles recordatorios</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default EventDetailPage;
