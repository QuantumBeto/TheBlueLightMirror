import math


class StaticWall:
    """
    Pared AABB axis-aligned para colisión.
    x1,z1 = esquina min   x2,z2 = esquina max
    """
    def __init__(self, x1, z1, x2, z2):
        self.x1, self.z1 = min(x1,x2), min(z1,z2)
        self.x2, self.z2 = max(x1,x2), max(z1,z2)


class CollisionSystem:
    @staticmethod
    def check_all(player, limits, obstacles, walls=None):
        collided  = False
        p_radio   = 0.5
        limit_x, limit_z = limits

        if player.x >  limit_x - p_radio: player.x =  limit_x - p_radio; collided = True
        if player.x < -limit_x + p_radio: player.x = -limit_x + p_radio; collided = True
        if player.z >  limit_z - p_radio: player.z =  limit_z - p_radio; collided = True
        if player.z < -limit_z + p_radio: player.z = -limit_z + p_radio; collided = True

        if walls:
            for w in walls:
                ex1 = w.x1 - p_radio; ex2 = w.x2 + p_radio
                ez1 = w.z1 - p_radio; ez2 = w.z2 + p_radio
                if ex1 < player.x < ex2 and ez1 < player.z < ez2:
                    # Empujar por el eje de menor penetración
                    ol = player.x - ex1   # overlap izquierda
                    or_ = ex2 - player.x  # overlap derecha
                    ot = player.z - ez1   # overlap arriba
                    ob = ez2 - player.z   # overlap abajo
                    mn = min(ol, or_, ot, ob)
                    if mn == ol:  player.x = ex1
                    elif mn == or_: player.x = ex2
                    elif mn == ot:  player.z = ez1
                    else:           player.z = ez2
                    collided = True

        for obs in obstacles:
            dx   = player.x - obs.x
            dz   = player.z - obs.z
            dist = math.sqrt(dx*dx + dz*dz)
            min_dist = obs.radius + p_radio
            if dist < min_dist:
                if dist == 0: dist = 0.001
                overlap = min_dist - dist
                player.x += (dx / dist) * overlap
                player.z += (dz / dist) * overlap
                if hasattr(obs, "tipo"):
                    if not hasattr(player, "concentracion"):
                        player.concentracion = 100.0
                    player.concentracion = max(0.0, player.concentracion - 0.5)
                collided = True

        return collided
