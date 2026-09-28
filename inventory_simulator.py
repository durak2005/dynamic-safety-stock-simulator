import numpy as np
import matplotlib.pyplot as plt

def calculate_rop_and_ss(avg_daily_demand, std_daily_demand, lead_time_days, service_level_z=1.65):
    """
    Hizmet seviyesine göre Güvenlik Stoğu (Safety Stock) ve 
    Yeniden Sipariş Noktası (Reorder Point - ROP) hesabı.
    Z = 1.65 (%95 Hizmet Seviyesi)
    """
    safety_stock = service_level_z * std_daily_demand * np.sqrt(lead_time_days)
    rop = (avg_daily_demand * lead_time_days) + safety_stock
    return safety_stock, rop

def run_inventory_simulation(days=50, initial_stock=250, order_qty=200, lead_time=3):
    avg_d = 20
    std_d = 5
    ss, rop = calculate_rop_and_ss(avg_d, std_d, lead_time)
    
    np.random.seed(42)
    daily_demands = np.random.normal(avg_d, std_d, days).round().astype(int)
    daily_demands = np.clip(daily_demands, 5, None)  # Negatif talep engelleme
    
    stock_levels = []
    current_stock = initial_stock
    order_in_transit = False
    delivery_day = -1
    order_days = []
    
    for day in range(days):
        if order_in_transit and day == delivery_day:
            current_stock += order_qty
            order_in_transit = False
            
        current_stock = max(0, current_stock - daily_demands[day])
        stock_levels.append(current_stock)
        
        if current_stock <= rop and not order_in_transit:
            order_in_transit = True
            delivery_day = day + lead_time
            order_days.append(day)
            
    return stock_levels, rop, ss, order_days

def plot_simulation(stock_levels, rop, ss, order_days):
    days = range(1, len(stock_levels) + 1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(days, stock_levels, color='#2563eb', linewidth=2, label='Eldeki Stok Seviyesi')
    ax.fill_between(days, stock_levels, color='#bfdbfe', alpha=0.4)
    
    ax.axhline(rop, color='#f59e0b', linestyle='--', linewidth=1.8, label=f'Yeniden Sipariş Noktası (ROP: {rop:.1f})')
    ax.axhline(ss, color='#ef4444', linestyle='--', linewidth=1.8, label=f'Güvenlik Stoğu (SS: {ss:.1f})')
    
    # Sipariş tetikleme günleri
    for od in order_days:
        ax.scatter(od + 1, stock_levels[od], color='#16a34a', s=80, zorder=5, label='Sipariş Tetiklendi' if od == order_days[0] else "")

    ax.set_title("50 Günlük Dinamik Envanter ve Güvenlik Stoğu Simülasyonu", fontsize=13, fontweight='bold')
    ax.set_xlabel("Günler", fontsize=11)
    ax.set_ylabel("Stok Miktarı (Adet)", fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig("inventory_simulation.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    stocks, rop_val, ss_val, orders = run_inventory_simulation()
    plot_simulation(stocks, rop_val, ss_val, orders)
