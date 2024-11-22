#include "e_epuck_ports.h"
#include "e_motors.h"
#include "e_prox.h"

int main() {
    e_init_port();
    e_init_motors();
    e_init_prox();

    while (1) {
        int ir_value = e_get_prox(0);  // Get value from proximity sensor 0

        e_set_speed_left(500);  // Set left motor speed
        e_set_speed_right(500); // Set right motor speed
    }
    return 0;
}
