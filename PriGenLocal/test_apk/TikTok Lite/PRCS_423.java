/*Application Package Name: com.tiktok.lite.go
class PRCS_423 {
/**
ms.bd.o.c1;L(I J Ljava/lang/String; Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final Object L(int p15, long p16, String p18, Object p19)
    {
        org.json.JSONArray v3_1 = new org.json.JSONArray();
        int v4_14 = ms.bd.o.a.L.LB.getApplicationContext();
        try {
            byte[] v13_5 = new byte[4];
            v13_5[0] = 98;
            v13_5[1] = 62;
            v13_5[2] = 76;
            v13_5[3] = 72;
            int v1_5 = ((android.net.wifi.WifiManager) v4_14.getSystemService(((String) ms.bd.o.k.a(16777217, 0, 0, "d59571", v13_5)))).getDhcpInfo();
            String v0_12 = new StringBuilder();
            v0_12.append((v1_5.dns1 & 255));
        } catch (Throwable) {
            byte[] v9_1 = new byte[6];
            v9_1 = {125, 106, 74, 115, 89, 122};
            ms.bd.o.k.a(16777217, 0, 0, "aa18ba", v9_1);
            return v3_1.toString();
        }
        byte[] v13_2 = new byte[1];
        v13_2[0] = 106;
        v0_12.append(((String) ms.bd.o.k.a(16777217, 0, 0, "55dd27", v13_2)));
        v0_12.append(((v1_5.dns1 >> 8) & 255));
        byte[] v13_3 = new byte[1];
        v13_3[0] = 109;
        v0_12.append(((String) ms.bd.o.k.a(16777217, 0, 0, "283cb3", v13_3)));
        v0_12.append(((v1_5.dns1 >> 16) & 255));
        byte[] v13_4 = new byte[1];
        v13_4[0] = 62;
        v0_12.append(((String) ms.bd.o.k.a(16777217, 0, 0, "ae4151", v13_4)));
        v0_12.append(((v1_5.dns1 >> 24) & 255));
        v3_1.put(v0_12.toString());
        String v0_16 = new StringBuilder();
        v0_16.append((v1_5.dns2 & 255));
        byte[] v13_6 = new byte[1];
        v13_6[0] = 109;
        v0_16.append(((String) ms.bd.o.k.a(16777217, 0, 0, "227378", v13_6)));
        v0_16.append(((v1_5.dns2 >> 8) & 255));
        byte[] v13_0 = new byte[1];
        v13_0[0] = 107;
        v0_16.append(((String) ms.bd.o.k.a(16777217, 0, 0, "4fe82f", v13_0)));
        v0_16.append(((v1_5.dns2 >> 16) & 255));
        byte[] v13_1 = new byte[1];
        v13_1[0] = 106;
        v0_16.append(((String) ms.bd.o.k.a(16777217, 0, 0, "546540", v13_1)));
        v0_16.append(((v1_5.dns2 >> 24) & 255));
        v3_1.put(v0_16.toString());
        return v3_1.toString();
    }


}