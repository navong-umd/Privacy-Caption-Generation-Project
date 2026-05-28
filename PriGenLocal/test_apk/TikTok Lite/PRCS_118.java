/*Application Package Name: com.tiktok.lite.go
class PRCS_118 {
/**
X.0cD;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyHacu2SzYe/7zTjpfgl8thoe1CgUDWai5Rr1Y=");
            com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
        } catch (android.net.NetworkInfo v0_3) {
            v0_3.printStackTrace();
            return X.1Mw.L();
        }
        if (!v1_0.intercept) {
            android.net.NetworkInfo v4_0 = p18.getActiveNetworkInfo();
            v3_1.postInvoke(v4_0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
X.0cD;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_20) {
            X.5If.L(v0_20);
            return X.0cD.L(p3);
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0cD.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.0cD.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0cD.L(p3);
                }
            } else {
                return X.0cD.L(p3);
            }
        } else {
            return X.0cD.L(p3);
        }
    }

/**
X.3rP;L(Ljava/lang/String; Ljava/lang/String; Ljava/lang/String; J J Z Lorg/json/JSONObject;)V
*/

    public final void L(String p22, String p23, String p24, long p25, long p27, boolean p29, org.json.JSONObject p30)
    {
        java.util.LinkedList v2 = com.ss.android.common.applog.AppLog.sInstance;
        if (v2 != null) {
            if ((X.0cE.L(p22)) || (X.0cE.L(p23))) {
                X.3sQ.L(1, 0, 0);
                return;
            } else {
                if (X.3rf.L()) {
                    if (X.69f.L == null) {
                        com.bytedance.ies.abmock.SettingsManager.L();
                        X.69f.L = kotlin.text.t.L(com.bytedance.ies.abmock.SettingsManager.L("core_offline_event", "video_play,play_time,publish"), new String[] {","}), 0, 0, 6, 0);
                    }
                    if (X.69f.L.contains(p23)) {
                        try {
                            org.json.JSONException v0_22 = X.0cD.LB(((android.net.ConnectivityManager) X.16B.LB.getSystemService("connectivity")));
                        } catch (Exception) {
                            org.json.JSONException v0_24 = 0;
                            try {
                                org.json.JSONException v0_25;
                                if (v0_24 == null) {
                                    v0_25 = "1";
                                    try {
                                        p30.put("isOffline", v0_25);
                                    } catch (org.json.JSONException v0_26) {
                                    }
                                    if (!X.5Vv.L) {
                                        if ((!X.3yY.L()) || (X.3yZ.L(p23))) {
                                            v2.onEvent(p22, p23, p24, p25, p27, p29, p30);
                                        }
                                    } else {
                                        if (X.69b.L == null) {
                                            com.bytedance.ies.abmock.SettingsManager.L();
                                            X.69b.L = kotlin.text.t.L(com.bytedance.ies.abmock.SettingsManager.L("applog_black_names", ""), new String[] {","}), 0, 0, 6, 0);
                                        }
                                        if (!X.69b.L.contains(p23)) {
                                        }
                                    }
                                    return;
                                } else {
                                    v0_25 = "0";
                                }
                            } catch (org.json.JSONException v0_26) {
                            }
                            v0_26.printStackTrace();
                        }
                        if ((v0_22 == null) || (!v0_22.isConnected())) {
                        } else {
                            v0_24 = 1;
                        }
                    }
                }
            }
        } else {
            String v3_0 = X.3rt.L();
            try {
                if (v3_0.L.size() > 200) {
                    org.json.JSONException v0_4 = ((X.3ro) v3_0.L.poll());
                    X.3sQ.L(1, 1, 0);
                    if (v0_4 != null) {
                        X.3rv.L().L(X.0Vu.CACHE_DROP_EVENT_COUNT);
                    }
                }
            } catch (org.json.JSONException v0_7) {
                throw v0_7;
            }
            v3_0.L.add(new X.3ro(p22, p23, p24, p25, p27, p29, p30));
            X.3sY.LC("AppLog null context when onEvent");
            return;
        }
    }


}