/*Application Package Name: com.tiktok.lite.go
class PRCS_136 {
/**
X.0Ic;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgAjS8/YVFkiQFyFaHCZkp+e+KI3kePSCIlq6CHqIYXJ2F/FTdUFhesRGBY8fpV7+Grf");
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
X.0Ic;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_20) {
            X.5If.L(v0_20);
            return X.0Ic.L(p3);
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0Ic.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.0Ic.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0Ic.L(p3);
                }
            } else {
                return X.0Ic.L(p3);
            }
        } else {
            return X.0Ic.L(p3);
        }
    }

/**
X.0Ic;LB()I
*/

    public final int LB()
    {
        if (!X.0Ic.LBL()) {
            if (!this.L()) {
                return -1;
            }
        } else {
            if (this.LB.isEmpty()) {
                return -1;
            }
        }
        boolean v0_18 = ((android.net.ConnectivityManager) this.LC.getSystemService("connectivity"));
        if (v0_18) {
            android.net.NetworkInfo v9_1 = X.0Ic.LB(v0_18);
            if ((v9_1 == null) || (!v9_1.isConnected())) {
                return -1;
            } else {
                int v3_2;
                com.bytedance.helios.statichook.api.HeliosApiHook v4_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v10_2 = new Object[0];
                com.bytedance.helios.statichook.api.ExtraInfo v11_4 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyFaHCZkp+e+KI3kePSCIlq6CHqIYXJ2F/FTdUFhesRGBY8fpV7+Grf");
                int v3_1 = v4_4.preInvoke(10216, "android/net/NetworkInfo", "getType", v9_1, v10_2, "int", v11_4);
                if (!v3_1.intercept) {
                    v3_2 = v9_1.getType();
                    v4_4.postInvoke(Integer.valueOf(v3_2), 10216, "android/net/NetworkInfo", "getType", v9_1, v10_2, v11_4, 1);
                } else {
                    v4_4.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v9_1, v10_2, v11_4, 0);
                    v3_2 = ((Integer) v3_1.returnValue).intValue();
                }
                if (v3_2 != 1) {
                    if (v3_2 != 0) {
                        return 1;
                    } else {
                        boolean v0_4;
                        com.bytedance.helios.statichook.api.HeliosApiHook v4_6 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v10_3 = new Object[0];
                        com.bytedance.helios.statichook.api.ExtraInfo v11_6 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgAjS8/YVFkiQFyFaHCZkp+e+KI3kePSCIlq6CHqIYXJ2F/FTdUFhesRGBY8fpV7+Grf");
                        int v3_3 = v4_6.preInvoke(10214, "android/net/NetworkInfo", "getSubtype", v9_1, v10_3, "int", v11_6);
                        if (!v3_3.intercept) {
                            v0_4 = v9_1.getSubtype();
                            v4_6.postInvoke(Integer.valueOf(v0_4), 10214, "android/net/NetworkInfo", "getSubtype", v9_1, v10_3, v11_6, 1);
                        } else {
                            v4_6.postInvoke(0, 10214, "android/net/NetworkInfo", "getSubtype", v9_1, v10_3, v11_6, 0);
                            v0_4 = ((Integer) v3_3.returnValue).intValue();
                        }
                        switch (v0_4) {
                            case 1:
                            case 2:
                            case 4:
                            case 7:
                            case 11:
                            case 16:
                                return 2;
                            case 3:
                            case 5:
                            case 6:
                            case 8:
                            case 9:
                            case 10:
                            case 12:
                            case 14:
                            case 15:
                            case 17:
                                return 3;
                            case 13:
                            case 18:
                                return 4;
                            case 19:
                            default:
                                String v5_1;
                                com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                Object[] v10_0 = new Object[0];
                                com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Ljava/lang/String;", "dzBzEgAjS8/YVFkiQFyFaHCZkp+e+KI3kePSCIlq6CHqIYXJ2F/FTdUFhesRGBY8fpV7+Grf");
                                com.bytedance.helios.statichook.api.Result v2_0 = v4_1.preInvoke(10215, "android/net/NetworkInfo", "getSubtypeName", v9_1, v10_0, "java.lang.String", v11_1);
                                if (!v2_0.intercept) {
                                    v5_1 = v9_1.getSubtypeName();
                                    v4_1.postInvoke(v5_1, 10215, "android/net/NetworkInfo", "getSubtypeName", v9_1, v10_0, v11_1, 1);
                                } else {
                                    v4_1.postInvoke(0, 10215, "android/net/NetworkInfo", "getSubtypeName", v9_1, v10_0, v11_1, 0);
                                    v5_1 = ((String) v2_0.returnValue);
                                }
                                if ((v5_1.equalsIgnoreCase("TD-SCDMA")) || ((v5_1.equalsIgnoreCase("WCDMA")) || (v5_1.equalsIgnoreCase("CDMA2000")))) {
                                    return 3;
                                } else {
                                    return 1;
                                }
                            case 20:
                                return 5;
                        }
                    }
                } else {
                    return 0;
                }
            }
        } else {
            return -1;
        }
    }


}