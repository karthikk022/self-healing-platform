import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

points = 60
minutes = np.linspace(0, 30, points)

sli = np.ones(points) * 0.998
sli[15:30] = np.linspace(0.998, 0.80, 15)
sli[30:45] = np.linspace(0.80, 0.97, 15)
sli[45:] = 0.995

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), gridspec_kw={'height_ratios': [3, 1]})

ax1.plot(minutes, sli * 100, color='#2563eb', linewidth=2.5, label='SLI (Success Rate)')
ax1.axhline(y=99.9, color='#22c55e', linestyle='--', linewidth=1.5, alpha=0.8, label='SLO Target (99.9%)')
ax1.axhline(y=99.0, color='#eab308', linestyle='--', linewidth=1.5, alpha=0.8, label='SLOTargetBreach (99%)')
ax1.axhline(y=95.0, color='#ef4444', linestyle='--', linewidth=1.5, alpha=0.8, label='HighErrorRate (95%)')

ax1.fill_between(minutes, sli * 100, 99.9, where=(sli * 100 < 99.9), color='#ef4444', alpha=0.15)
ax1.fill_between(minutes, sli * 100, 95, where=(sli * 100 < 95), color='#ef4444', alpha=0.3)

ax1.axvspan(8, 15, alpha=0.08, color='#ef4444', label='Error injection')
ax1.axvspan(15, 18, alpha=0.12, color='#22c55e', label='Remediation trigger')

ax1.annotate('ERROR_RATE=0.4 injected\n→ 40% 5xx errors', xy=(12, 87),
            fontsize=8, color='#ef4444', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#ef4444', alpha=0.9))
ax1.annotate('Alertmanager webhook\n→ Scale 2→5 + restart', xy=(17, 82),
            fontsize=8, color='#22c55e', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#22c55e', alpha=0.9))
ax1.annotate('Recovery complete\nSLI back above SLO', xy=(24, 98.5),
            fontsize=8, color='#2563eb', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#2563eb', alpha=0.9))

ax1.set_ylabel('Success Rate (%)', fontsize=10)
ax1.set_ylim(75, 101)
ax1.legend(loc='lower left', fontsize=7, ncol=2)
ax1.grid(True, alpha=0.3)
ax1.set_title('SLO Breach → Auto-Remediation → Recovery', fontsize=13, fontweight='bold', pad=15)

replicas = np.ones(points) * 2
replicas[30:46] = 5
replicas[46:] = 2

ax2.step(minutes, replicas, where='post', color='#2563eb', linewidth=2.5)
ax2.set_ylabel('Pods', fontsize=10)
ax2.set_xlabel('Time (minutes)', fontsize=10)
ax2.set_ylim(0, 7)
ax2.set_yticks([2, 5])
ax2.grid(True, alpha=0.3)
ax2.axvspan(15, 22, alpha=0.12, color='#22c55e')
ax2.annotate('Scale up\n2 → 5', xy=(17, 5), fontsize=9, color='#2563eb', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#2563eb', alpha=0.9))

plt.tight_layout()
plt.savefig('C:\\Users\\User\\projects\\self-healing-platform\\docs\\slo-recovery-demo.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved to docs/slo-recovery-demo.png")
