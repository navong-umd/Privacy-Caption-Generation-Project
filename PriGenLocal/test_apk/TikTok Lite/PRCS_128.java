/*Application Package Name: com.tiktok.lite.go
class PRCS_128 {
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
X.0cD;LCC(Landroid/content/Context;)LX/0cB;
*/

    public static X.0cB LCC(android.content.Context p2)
    {
        try {
            int v1_2 = X.0cD.LB(((android.net.ConnectivityManager) p2.getSystemService("connectivity")));
        } catch (Throwable) {
            return X.0cB.MOBILE;
        }
        if ((v1_2 == 0) || (!v1_2.isAvailable())) {
            return X.0cB.NONE;
        } else {
            int v1_0 = X.0cD.L(v1_2, "dzBzEgAjS8/YVFkiQFyHacu2SzYe/7zTjpfgl8thoe1CgUDWai5Rr1Y=");
            if (1 != v1_0) {
                if (v1_0 != 0) {
                    return X.0cB.MOBILE;
                } else {
                    int v1_1 = X.0cD.L(((android.telephony.TelephonyManager) p2.getSystemService("phone")));
                    if (v1_1 != 3) {
                        if (v1_1 == 20) {
                            return X.0cB.MOBILE_5G;
                        } else {
                            if ((v1_1 != 5) && (v1_1 != 6)) {
                                switch (v1_1) {
                                    case 8:
                                    case 9:
                                    case 10:
                                    case 8:
                                    case 9:
                                    case 10:
                                        break;
                                    case 8:
                                    case 9:
                                    case 10:
                                        break;
                                    default:
                                        switch (v1_1) {
                                            case 12:
                                            case 14:
                                            case 15:
                                                break;
                                            case 13:
                                                return X.0cB.MOBILE_4G;
                                            case 12:
                                            case 14:
                                            case 15:
                                                break;
                                            case 12:
                                            case 14:
                                            case 15:
                                                break;
                                            default:
                                                return X.0cB.MOBILE;
                                        }
                                }
                            }
                        }
                    }
                    return X.0cB.MOBILE_3G;
                }
            } else {
                return X.0cB.WIFI;
            }
        }
    }


}