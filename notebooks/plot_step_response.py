import sys, numpy as np, control as ct, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# Parvalux PM7S model, values from notebooks/SIM_Moteurs_Parvalux.ipynb
R, Km, J, f = 4.9, 43e-3, 3.61e-5, 2.9e-4
s = ct.tf('s'); Mt = Km / (Km**2 + (f + J*s) * R)
Mt_rpm = (60/(2*np.pi)) * Mt
Te = 0.005; Mz = ct.c2d(Mt_rpm, Te, 'zoh')
Kp, Ki, Kd = 0.039, 0.005, 0.01
z = ct.tf([1, 0], [1], Te); Cz = Kp + Ki*z/(z-1) + Kd*(z-1)/z
T = ct.feedback(Cz*Mz, 1)
t = np.arange(0, 0.6, Te)
t1, y1 = ct.step_response(T*3000, t)
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=130)
ax.step(t1, y1, where='post', lw=2, label='closed loop with discrete PID (Te = 5 ms)')
ax.axhline(3000, color='gray', ls='--', lw=1, label='setpoint 3000 rpm')
ax.set_xlabel('time (s)'); ax.set_ylabel('motor speed (rpm)')
ax.set_title('Parvalux PM7S speed loop: step response'); ax.grid(alpha=.3); ax.legend(loc='lower right')
fig.tight_layout(); fig.savefig(sys.argv[1]); print('ok', y1[-1])
