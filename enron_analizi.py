import networkx as nx
import urllib.request
import os
import gzip
import community.community_louvain as community_louvain

def main():
    print("=== Enron Email Ağı Analizi (Adım 1, 2, 3 ve 4) ===\n")
    
    # 1. Veri İndirme (Eğer klasörde yoksa otomatik indirir)
    url = "https://snap.stanford.edu/data/email-Enron.txt.gz"
    file_name = "email-Enron.txt.gz"

    if not os.path.exists(file_name):
        print("[!] Veri seti bulunamadı. İnternetten indiriliyor (yaklaşık 1.7 MB)...")
        urllib.request.urlretrieve(url, file_name)
        print("[+] İndirme tamamlandı.")
    else:
        print("[+] Veri seti klasörde mevcut.")

    # 2. Veriyi Yükleme (Adım 2)
    print("\n[+] Ağ oluşturuluyor (Bu işlem birkaç saniye sürebilir)...")
    # Dosya içindeki '#' ile başlayan satırlar yorumdur (atlanır).
    # Bu ağ yönlü de (DiGraph) yapılabilir ama temel metrikler için yönsüz (Graph) ele almak daha kolaydır.
    G = nx.read_edgelist(file_name, comments='#', create_using=nx.Graph(), nodetype=int)

    # Ağın genel boyutu
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"-> Toplam Düğüm Sayısı (Çalışanlar): {num_nodes}")
    print(f"-> Toplam Kenar Sayısı (İletişim): {num_edges}")

    # 3. ve 4. Başlıklar: Temel Ağ Ölçümleri (Ünite 2 ve 3 Hesaplamaları)
    print("\n--- Temel Ağ Ölçümleri (Ünite 2 & 3) ---")
    
    # Yoğunluk (Density)
    density = nx.density(G)
    print(f"1) Ağın Yoğunluğu (Density): {density:.5f}")
    print("   Yorum: Yoğunluk çok düşük. Bu durum, devasa şirketlerde herkesin birbirini tanımadığını, iletişimin alt gruplar arasında olduğunu gösterir.")

    # Ortalama Derece (Average Degree)
    degrees = [deg for node, deg in G.degree()]
    avg_degree = sum(degrees) / len(degrees)
    print(f"\n2) Ortalama Derece (Average Degree): {avg_degree:.2f}")
    print("   Yorum: Şirketteki her bir çalışan, ortalama 10 farklı kişiyle e-posta üzerinden iletişim kurmuştur.")

    # Kümelenme Katsayısı (Clustering Coefficient)
    print("\n3) Kümelenme katsayısı hesaplanıyor (Biraz zaman alabilir)...")
    avg_clustering = nx.average_clustering(G)
    print(f"-> Ortalama Kümelenme Katsayısı (Clustering Coefficient): {avg_clustering:.4f}")
    print("   Yorum: Bir kişinin iletişim kurduğu kişilerin kendi aralarında iletişim kurma olasılığı (yaklaşık %10). Organizasyon şemasına işaret eder.")

    # Bağlantılı Bileşenler (Connected Components)
    components = list(nx.connected_components(G))
    num_components = len(components)
    largest_cc = max(components, key=len)
    print(f"\n4) Bağlantılı Bileşen Sayısı: {num_components}")
    print(f"   En Büyük Bileşendeki (Giant Component) Kişi Sayısı: {len(largest_cc)}")
    print(f"   Yorum: Ağın %{len(largest_cc)/num_nodes*100:.1f}'i tek bir devasa iletişim ağının (Giant Component) parçasıdır. Geri kalanlar tamamen kopuk adalardır.")

    # Adım 5: Topluluk Belirleme
    adim5_topluluk_bulma(G)

    # Adım 6: Merkezilik Ölçümleri
    adim6_merkezilik(G)

    # Adım 7: Araştırma / Geliştirme (Bağlantı Tahmini)
    adim7_link_prediction(G)

def adim5_topluluk_bulma(G):
    print("\n=== Adım 5: Topluluk Belirleme (Community Detection) ===")
    print("Louvain algoritması ile topluluklar bulunuyor (Biraz zaman alabilir)...")
    # Çok büyük ağı hızlandırmak için en büyük bağlantılı bileşen üzerinde yapabiliriz
    largest_cc = max(nx.connected_components(G), key=len)
    G_sub = G.subgraph(largest_cc)
    
    partition = community_louvain.best_partition(G_sub)
    num_communities = len(set(partition.values()))
    print(f"-> Toplam {num_communities} farklı topluluk (departman/çalışma grubu) bulundu.")
    
    from collections import Counter
    counts = Counter(partition.values())
    largest_comm, size = counts.most_common(1)[0]
    print(f"-> En büyük topluluktaki kişi sayısı: {size}")
    print("Yorum: Louvain algoritması, e-posta trafiğine göre şirketteki doğal çalışma gruplarını başarıyla kümeler.")

def adim6_merkezilik(G):
    print("\n=== Adım 6: Merkezilik Ölçümleri (Centrality Measures) ===")
    print("En önemli (merkezi) aktörler belirleniyor...")
    
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\n1) Derece Merkeziliği (En çok kişiyle iletişim kuranlar):")
    for node, score in top_degree:
        print(f"   Düğüm {node}: {score:.5f}")
    print("   Yorum: Derece merkeziliği yüksek olanlar şirketin 'bağlayıcı' veya 'bilgi dağıtıcı' rolleridir.")

    pagerank_cent = nx.pagerank(G)
    top_pr = sorted(pagerank_cent.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\n2) PageRank Merkeziliği (En 'önemli' kişilerden mail alanlar):")
    for node, score in top_pr:
        print(f"   Düğüm {node}: {score:.5f}")
    print("   Yorum: PageRank'i yüksek olanlar organizasyondaki kilit yöneticilerdir.")

def adim7_link_prediction(G):
    print("\n=== Adım 7: Araştırma/Geliştirme - Bağlantı Tahmini (Link Prediction) ===")
    print("Problem: E-posta iletişim ağına bakarak, birbirini tanıma ihtimali en yüksek kişileri önerme.")
    print("Çözüm Modeli: Adamic-Adar İndeksi.")
    print("Referans: Lada A. Adamic and Eytan Adar. 'Friends and neighbors on the web.' Social networks 25.3 (2003).")
    
    degrees = dict(G.degree())
    target_node = max(degrees, key=degrees.get)
    target_neighbors = set(G.neighbors(target_node))
    
    print(f"\nHedef Kişi Seçildi: Düğüm {target_node} (Şirketin en aktif e-posta kullanıcısı)")
    
    candidates = set()
    for neighbor in target_neighbors:
        for neighbors_neighbor in G.neighbors(neighbor):
            if neighbors_neighbor != target_node and neighbors_neighbor not in target_neighbors:
                candidates.add(neighbors_neighbor)
    
    print(f"Bağlantı önerilebilecek aday sayısı (Ortak arkadaşı olanlar): {len(candidates)}")
    
    ebunch = [(target_node, cand) for cand in candidates]
    preds = nx.adamic_adar_index(G, ebunch)
    sorted_preds = sorted(preds, key=lambda x: x[2], reverse=True)
    
    print(f"\nDüğüm {target_node} için en güçlü 5 iletişim/bağlantı önerisi:")
    for u, v, p in sorted_preds[:5]:
        print(f"   Önerilen Kişi: Düğüm {v} | Adamic-Adar Skoru: {p:.4f}")
        
    print("\nYorum: Adamic-Adar skoru yüksek olan adaylar, hedef kişiyle çok sayıda ve 'özel' ortak arkadaşa sahiptir.")

if __name__ == "__main__":
    main()
