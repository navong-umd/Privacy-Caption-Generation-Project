/*Application Package Name: com.tiktok.lite.go
class PRCS_301 {
/**
X.0hG;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyHdNRwud8ndmm3vk6QYQ==");
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
X.0hG;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_19) {
            X.5If.L(v0_19);
            return X.0hG.L(p3);
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uL.LB()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0hG.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uL.LBL()) {
                            X.5uL.L("cm_net_info", X.0hG.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0hG.L(p3);
                }
            } else {
                return X.0hG.L(p3);
            }
        } else {
            return X.0hG.L(p3);
        }
    }

/**
X.0hG;L()I
*/

    public static int L()
    {
        try {
            int v0_13 = X.0fV.L().L;
        } catch (Throwable) {
            return 0;
        }
        if (v0_13 != 0) {
            int v3_7 = X.0hG.L(v0_13);
            if (v3_7 != 0) {
                android.telephony.TelephonyManager v10_0 = X.0hG.LB(v3_7);
                if ((v10_0 == null) || (!v10_0.isAvailable())) {
                    return 0;
                } else {
                    int v3_2;
                    com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                    Object[] v11_0 = new Object[0];
                    com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyHdNRwud8ndmm3vk6QYQ==");
                    int v4_0 = v5_1.preInvoke(10216, "android/net/NetworkInfo", "getType", v10_0, v11_0, "int", v12_1);
                    if (!v4_0.intercept) {
                        v3_2 = v10_0.getType();
                        v5_1.postInvoke(Integer.valueOf(v3_2), 10216, "android/net/NetworkInfo", "getType", v10_0, v11_0, v12_1, 1);
                    } else {
                        v5_1.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v10_0, v11_0, v12_1, 0);
                        v3_2 = ((Integer) v4_0.returnValue).intValue();
                    }
                    if (1 != v3_2) {
                        if (v3_2 != 0) {
                            return 2;
                        } else {
                            int v1_1;
                            android.telephony.TelephonyManager v10_2 = ((android.telephony.TelephonyManager) v0_13.getSystemService("phone"));
                            if (android.os.Build$VERSION.SDK_INT < 29) {
                                com.bytedance.helios.statichook.api.HeliosApiHook v5_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                Object[] v11_1 = new Object[0];
                                com.bytedance.helios.statichook.api.ExtraInfo v12_3 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyHdNRwud8ndmm3vk6QYQ==");
                                int v1_2 = v5_4.preInvoke(102013, "android/telephony/TelephonyManager", "getNetworkType", v10_2, v11_1, "int", v12_3);
                                if (!v1_2.intercept) {
                                    v1_1 = v10_2.getNetworkType();
                                    v5_4.postInvoke(Integer.valueOf(v1_1), 102013, "android/telephony/TelephonyManager", "getNetworkType", v10_2, v11_1, v12_3, 1);
                                } else {
                                    v5_4.postInvoke(0, 102013, "android/telephony/TelephonyManager", "getNetworkType", v10_2, v11_1, v12_3, 0);
                                    v1_1 = ((Integer) v1_2.returnValue).intValue();
                                }
                            } else {
                                if (!X.5W7.L.getAndSet(1)) {
                                    X.5W7.L().LB();
                                }
                                v1_1 = X.5W7.L().L();
                                if ((!X.5W7.LB) && (v1_1 == -1)) {
                                    return 2;
                                }
                            }
                            switch (v1_1) {
                                case 2:
                                    return 3;
                                case 3:
                                case 5:
                                case 6:
                                case 8:
                                case 9:
                                case 10:
                                case 12:
                                case 14:
                                case 15:
                                    return 4;
                                case 4:
                                case 7:
                                case 11:
                                case 16:
                                case 17:
                                case 18:
                                case 19:
                                default:
                                    return 2;
                                case 13:
                                    return 5;
                                case 20:
                                    return 6;
                            }
                        }
                    } else {
                        return 1;
                    }
                }
            } else {
                return 0;
            }
        } else {
            return 0;
        }
    }


}