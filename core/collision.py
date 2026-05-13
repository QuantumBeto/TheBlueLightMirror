import math

class CollisionSystem:
    @staticmethod
    def check_all(player, limits, obstacles):
        """
        Verifica colisiones del jugador contra los bordes del mapa y una lista de objetos.
        limits = (limite_x, limite_z)
        """
        collided = False
        p_radio = 0.5
        limit_x, limit_z = limits

        # 1. Colisión con los límites del mapa (AABB)
        if player.x >  limit_x - p_radio: player.x =  limit_x - p_radio; collided = True
        if player.x < -limit_x + p_radio: player.x = -limit_x + p_radio; collided = True
        if player.z >  limit_z - p_radio: player.z =  limit_z - p_radio; collided = True
        if player.z < -limit_z + p_radio: player.z = -limit_z + p_radio; collided = True

        # 2. Colisión con objetos del mundo (Muebles, Distracciones, NPCs)
        for obs in obstacles:
            # Asumimos que todo objeto interactuable tiene x, z y radius
            dx = player.x - obs.x
            dz = player.z - obs.z
            dist = math.sqrt(dx*dx + dz*dz)
            min_dist = obs.radius + p_radio
            
            if dist < min_dist:
                if dist == 0: dist = 0.001
                overlap = min_dist - dist
                # Efecto de deslizarse suavemente
                player.x += (dx / dist) * overlap
                player.z += (dz / dist) * overlap
                
                # Fricción Cognitiva: Solo restar concentración si el objeto es una Distracción Digital
                if hasattr(obs, "tipo"):
                    if not hasattr(player, "concentracion"): player.concentracion = 100.0
                    player.concentracion = max(0.0, player.concentracion - 0.5)
                
                collided = True

        return collided