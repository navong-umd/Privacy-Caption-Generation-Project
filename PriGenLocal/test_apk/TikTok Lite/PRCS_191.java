/*Application Package Name: com.tiktok.lite.go
class PRCS_191 {
/**
X.0ds;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyHacu2SzYe/bvZip/6gIBD6urZ0ODyQS8INHkD+ZAwhwr/yW8=");
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
X.0ds;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_19) {
            X.5If.L(v0_19);
            return X.0ds.L(p3);
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uL.LB()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0ds.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uL.LBL()) {
                            X.5uL.L("cm_net_info", X.0ds.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0ds.L(p3);
                }
            } else {
                return X.0ds.L(p3);
            }
        } else {
            return X.0ds.L(p3);
        }
    }

/**
X.0ds;LB(Landroid/content/Context;)LX/0dr;
*/

    public static X.0dr LB(android.content.Context p19)
    {
        try {
            android.net.NetworkInfo v9 = X.0ds.LB(((android.net.ConnectivityManager) p19.getSystemService("connectivity")));
        } catch (Throwable) {
            return X.0dr.MOBILE;
        }
        if ((v9 == null) || (!v9.isAvailable())) {
            return X.0dr.NONE;
        } else {
            android.telephony.TelephonyManager v2_2;
            com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v10 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyHacu2SzYe/bvZip/6gIBD6urZ0ODyQS8INHkD+ZAwhwr/yW8=");
            android.telephony.TelephonyManager v2_1 = v4_1.preInvoke(10216, "android/net/NetworkInfo", "getType", v9, v10, "int", v11_1);
            if (!v2_1.intercept) {
                v2_2 = v9.getType();
                v4_1.postInvoke(Integer.valueOf(v2_2), 10216, "android/net/NetworkInfo", "getType", v9, v10, v11_1, 1);
            } else {
                v4_1.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v9, v10, v11_1, 0);
                v2_2 = ((Integer) v2_1.returnValue).intValue();
            }
            if (1 != v2_2) {
                if (v2_2 != null) {
                    return X.0dr.MOBILE;
                } else {
                    android.telephony.TelephonyManager v2_4 = ((android.telephony.TelephonyManager) p19.getSystemService("phone"));
                    if (v2_4 != null) {
                        if ((X.0ds.L(v2_4) == 3) || ((X.0ds.L(v2_4) == 5) || ((X.0ds.L(v2_4) == 6) || ((X.0ds.L(v2_4) == 8) || ((X.0ds.L(v2_4) == 9) || ((X.0ds.L(v2_4) == 10) || ((X.0ds.L(v2_4) == 12) || ((X.0ds.L(v2_4) == 14) || (X.0ds.L(v2_4) == 15))))))))) {
                            return X.0dr.MOBILE_3G;
                        } else {
                            if (X.0ds.L(v2_4) != 13) {
                                return X.0dr.MOBILE;
                            } else {
                                return X.0dr.MOBILE_4G;
                            }
                        }
                    } else {
                        return X.0dr.MOBILE;
                    }
                }
            } else {
                return X.0dr.WIFI;
            }
        }
    }


}