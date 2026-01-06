import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getNextEvent, getRecentActivity } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Calendar, 
  Users, 
  Bell, 
  Clock, 
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Loader2,
  CalendarDays,
  Send,
  Plus
} from 'lucide-react';
import { motion } from 'framer-motion';
import { format, formatDistanceToNow, parseISO, differenceInDays, differenceInHours, differenceInMinutes } from 'date-fns';
import { es } from 'date-fns/locale';

const StatCard = ({ title, value, icon: Icon, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
  >
    <Card className="hover:border-primary/50 transition-colors duration-300">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="w-4 h-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  </motion.div>
);

const CountdownTimer = ({ eventDate }) => {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0 });

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const event = parseISO(eventDate);
      
      const days = differenceInDays(event, now);
      const hours = differenceInHours(event, now) % 24;
      const minutes = differenceInMinutes(event, now) % 60;
      
      setTimeLeft({ days, hours, minutes });
    };

    calculateTimeLeft();
    const interval = setInterval(calculateTimeLeft, 60000);
    return () => clearInterval(interval);
  }, [eventDate]);

  return (
    <div className="flex items-center gap-4">
      <div className="text-center">
        <div className="text-4xl font-bold font-mono text-primary">{timeLeft.days}</div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider">Días</div>
      </div>
      <div className="text-2xl text-muted-foreground">:</div>
      <div className="text-center">
        <div className="text-4xl font-bold font-mono text-primary">{timeLeft.hours}</div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider">Horas</div>
      </div>
      <div className="text-2xl text-muted-foreground">:</div>
      <div className="text-center">
        <div className="text-4xl font-bold font-mono text-primary">{timeLeft.minutes}</div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider">Min</div>
      </div>
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const variants = {
    sent: { className: 'bg-green-500/20 text-green-500 border-green-500/30', label: 'Enviado' },
    pending: { className: 'bg-amber-500/20 text-amber-500 border-amber-500/30', label: 'Pendiente' },
    failed: { className: 'bg-red-500/20 text-red-500 border-red-500/30', label: 'Fallido' },
  };

  const variant = variants[status] || variants.pending;

  return (
    <Badge variant="outline" className={variant.className}>
      {status === 'sent' && <CheckCircle className="w-3 h-3 mr-1" />}
      {status === 'pending' && <Clock className="w-3 h-3 mr-1" />}
      {status === 'failed' && <AlertCircle className="w-3 h-3 mr-1" />}
      {variant.label}
    </Badge>
  );
};

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [nextEvent, setNextEvent] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, nextEventRes, activityRes] = await Promise.all([
          getDashboardStats(),
          getNextEvent(),
          getRecentActivity(5)
        ]);
        setStats(statsRes.data);
        setNextEvent(nextEventRes.data);
        setRecentActivity(activityRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="dashboard-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Resumen de tus eventos y notificaciones
          </p>
        </div>
        <Link to="/events">
          <Button className="glow-primary-hover" data-testid="new-event-btn">
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Evento
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Eventos"
          value={stats?.total_events || 0}
          icon={Calendar}
          description="Eventos creados"
          delay={0.1}
        />
        <StatCard
          title="Próximos Eventos"
          value={stats?.upcoming_events || 0}
          icon={CalendarDays}
          description="Por realizar"
          delay={0.15}
        />
        <StatCard
          title="Contactos"
          value={stats?.total_contacts || 0}
          icon={Users}
          description="Registrados"
          delay={0.2}
        />
        <StatCard
          title="Notificaciones"
          value={stats?.sent_notifications || 0}
          icon={Send}
          description="Enviadas"
          delay={0.25}
        />
      </div>

      {/* Main Content Grid (Bento) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Next Event - Large Hero Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-8"
        >
          <Card className="h-full border-primary/20 hover:border-primary/50 transition-colors duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardDescription className="text-xs uppercase tracking-[0.2em] text-primary">
                    Próximo Evento
                  </CardDescription>
                  <CardTitle className="text-2xl mt-1">
                    {nextEvent ? nextEvent.title : 'Sin eventos próximos'}
                  </CardTitle>
                </div>
                {nextEvent && (
                  <Link to={`/events/${nextEvent.id}`}>
                    <Button variant="outline" size="sm" data-testid="view-next-event-btn">
                      Ver detalles
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {nextEvent ? (
                <div className="space-y-6">
                  <CountdownTimer eventDate={nextEvent.event_date} />
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-4 border-t border-border">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Fecha</p>
                      <p className="font-mono text-sm">
                        {format(parseISO(nextEvent.event_date), "dd MMM yyyy", { locale: es })}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Hora</p>
                      <p className="font-mono text-sm">
                        {format(parseISO(nextEvent.event_date), "HH:mm", { locale: es })}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Suscriptores</p>
                      <p className="font-mono text-sm">{nextEvent.subscribers_count || 0}</p>
                    </div>
                  </div>

                  {nextEvent.description && (
                    <p className="text-sm text-muted-foreground">
                      {nextEvent.description}
                    </p>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
                    <Calendar className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <p className="text-muted-foreground mb-4">
                    No tienes eventos programados
                  </p>
                  <Link to="/events">
                    <Button data-testid="create-first-event-btn">
                      <Plus className="w-4 h-4 mr-2" />
                      Crear primer evento
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="lg:col-span-4"
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-lg">Estado de Notificaciones</CardTitle>
              <CardDescription>Resumen de envíos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-500" />
                  <span className="text-sm">Pendientes</span>
                </div>
                <span className="font-mono font-bold">{stats?.pending_notifications || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-sm">Enviadas</span>
                </div>
                <span className="font-mono font-bold">{stats?.sent_notifications || 0}</span>
              </div>
              <div className="pt-4 border-t border-border">
                <Link to="/notifications">
                  <Button variant="outline" className="w-full" data-testid="view-all-notifications-btn">
                    Ver todas las notificaciones
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-12"
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Actividad Reciente</CardTitle>
                  <CardDescription>Últimas notificaciones procesadas</CardDescription>
                </div>
                <Link to="/notifications">
                  <Button variant="ghost" size="sm">
                    Ver todo
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {recentActivity.length > 0 ? (
                <div className="space-y-3">
                  {recentActivity.map((activity, index) => (
                    <div
                      key={activity.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                          <Bell className="w-5 h-5 text-muted-foreground" />
                        </div>
                        <div>
                          <p className="text-sm font-medium">{activity.event_title}</p>
                          <p className="text-xs text-muted-foreground">
                            Para: {activity.contact_name}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <StatusBadge status={activity.status} />
                        <span className="text-xs text-muted-foreground font-mono">
                          {activity.scheduled_at && formatDistanceToNow(parseISO(activity.scheduled_at), { addSuffix: true, locale: es })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No hay actividad reciente</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;
