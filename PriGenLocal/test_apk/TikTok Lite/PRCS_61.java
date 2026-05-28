/*Application Package Name: com.tiktok.lite.go
class PRCS_61 {
/**
X.0Un;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p0)
    {
        try {
            return p0.getActiveNetworkInfo();
        } catch (android.net.NetworkInfo v0_2) {
            v0_2.printStackTrace();
            return X.1Mw.L();
        }
    }

/**
X.0Un;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_19) {
            X.5If.L(v0_19);
            return X.0Un.L(p3);
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uL.LB()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0Un.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uL.LBL()) {
                            X.5uL.L("cm_net_info", X.0Un.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0Un.L(p3);
                }
            } else {
                return X.0Un.L(p3);
            }
        } else {
            return X.0Un.L(p3);
        }
    }

/**
X.1r1;L(Lorg/json/JSONObject; Z)V
*/

    private void L(org.json.JSONObject p14, boolean p15)
    {
        try {
            if (!android.text.TextUtils.isEmpty(X.1rF.LFI())) {
                p14.put("session_id", X.1rF.LFI());
            }
        } catch (Exception) {
            return;
        }
        if (p14.isNull("network_type")) {
            int v1_3 = X.0cD.LBL(X.0UX.LCCII);
            p14.put("network_type", v1_3.L);
            if ((v1_3 == X.0cB.MOBILE) || ((v1_3 == X.0cB.MOBILE_2G) || ((v1_3 == X.0cB.MOBILE_3G) || ((v1_3 == X.0cB.MOBILE_3G_H) || ((v1_3 == X.0cB.MOBILE_3G_HP) || ((v1_3 == X.0cB.MOBILE_4G) || (v1_3 == X.0cB.MOBILE_5G))))))) {
                java.io.File v3_2 = X.0UX.LCCII;
                long v2_6 = this.LCC;
                if (X.04U.L(v3_2, "android.permission.ACCESS_NETWORK_STATE") == 0) {
                    int v1_6 = X.0Un.LB(((android.net.ConnectivityManager) v3_2.getSystemService("connectivity")));
                    if ((v1_6 != 0) && ((v1_6.isAvailable()) && ((v1_6.getType() == 0) && (v2_6 != 0)))) {
                        int v1_7 = ((Integer) v2_6.L(v3_2)).intValue();
                        if (v1_7 != -10000) {
                            p14.put("network_type_code", v1_7);
                        }
                    }
                }
            }
        }
        if ((p14.isNull("timestamp")) || (p14.optLong("timestamp") <= 0)) {
            p14.put("timestamp", System.currentTimeMillis());
        }
        if (p14.isNull("sid")) {
            p14.put("sid", X.1rF.L());
        }
        p14.put("process_name", X.1rF.LC());
        if (!p15) {
            return;
        } else {
            String v0_7;
            X.0TG v4 = X.0Sv.L;
            if (v4.L != null) {
                String v0_10 = v4.L;
                if (v0_10 == null) {
                    v0_7 = v4.LB;
                    v4.LB = (1 + v0_7);
                } else {
                    String v0_12 = (v0_10.getLong(0) + 1);
                    v4.LB = v0_12;
                    v4.L.putLong(0, v0_12);
                    v0_7 = v4.LB;
                }
            } else {
                long v2_7 = X.1rF.LC();
                java.io.File v3_5 = new StringBuilder();
                v3_5.append(v2_7.replace(".", "_").replace(":", "-"));
                v3_5.append("_seq_num.txt");
                java.io.File v3_1 = new java.io.File(X.0Sn.L(), v3_5.toString());
                long v2_1 = v3_1.exists();
                if (v2_1 == 0) {
                    v3_1.createNewFile();
                }
                String v0_6 = new java.io.RandomAccessFile(v3_1, "rw").getChannel().map(java.nio.channels.FileChannel$MapMode.READ_WRITE, 0, 8);
                v4.L = v0_6;
                if (v2_1 != 0) {
                } else {
                    v0_6.putLong(0, 0);
                    v0_7 = 0;
                }
            }
            p14.put("seq_no", v0_7);
            return;
        }
    }


}