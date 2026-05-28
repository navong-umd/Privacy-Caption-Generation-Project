/*Application Package Name: com.tiktok.lite.go
class PRCS_232 {
/**
X.3PS;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28eZ");
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
X.3Py;run()V
*/

    public final void run()
    {
        java.net.URL v5_0 = this.L;
        v5_0.ac_();
        if (v5_0.LIIII.LF().LFI.L()) {
            v5_0.LIIII.ag_().LFF.L("Deferred Deep Link already retrieved. Not fetching again.");
            return;
        } else {
            String v3_3 = v5_0.LIIII.LF().LFLL.L();
            v5_0.LIIII.LF().LFLL.L((1 + v3_3));
            if (v3_3 < 5) {
                java.net.URL v5_3;
                String v0_29 = v5_0.LIIII;
                v0_29.ah_().ac_();
                X.3PS.L(v0_29.LIIIIZZ);
                X.3PS.L(v0_29.LIIIIZZ);
                X.3PS.L(v0_29.LIIJILLL);
                X.3Oo v2_2 = v0_29.LIIJILLL.LCC();
                X.3PS.L(v0_29.LII);
                String v1_65 = v0_29.LII;
                v1_65.ac_();
                X.3Rf v6_4 = v1_65.LIIII.LFF.LB();
                String v9_4 = v1_65.LIIIII;
                if ((v9_4 == null) || (v6_4 >= v1_65.LIIIIZZ)) {
                    v1_65.LIIIIZZ = (v6_4 + v1_65.LIIII.LCCII.LBL(v2_2, X.3Oc.LB));
                    try {
                        String v9_1;
                        X.3Rf v6_6 = v1_65.LIIII.L;
                        int v8_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v14 = new Object[1];
                        v14[0] = v6_6;
                        com.bytedance.helios.statichook.api.ExtraInfo v15_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Context;)Lcom/google/android/gms/ads/identifier/AdvertisingIdClient$Info;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28aW");
                        java.net.URL v5_10 = v8_3.preInvoke(103000, "com/google/android/gms/ads/identifier/AdvertisingIdClient", "getAdvertisingIdInfo", com.google.android.gms.a.a.a, v14, "com.google.android.gms.ads.identifier.AdvertisingIdClient$Info", v15_1);
                    } catch (X.3Rf v6_0) {
                        v1_65.LIIII.ag_().LFF.L("Unable to get advertising id", v6_0);
                        v1_65.LIIIII = "";
                        v5_3 = new android.util.Pair(v1_65.LIIIII, Boolean.valueOf(v1_65.LIIIIZ));
                    }
                    if (!v5_10.intercept) {
                        v9_1 = com.google.android.gms.a.a.a.L(v6_6);
                        v8_3.postInvoke(v9_1, 103000, "com/google/android/gms/ads/identifier/AdvertisingIdClient", "getAdvertisingIdInfo", com.google.android.gms.a.a.a, v14, v15_1, 1);
                    } else {
                        v8_3.postInvoke(0, 103000, "com/google/android/gms/ads/identifier/AdvertisingIdClient", "getAdvertisingIdInfo", com.google.android.gms.a.a.a, v14, v15_1, 0);
                        v9_1 = ((X.37G) v5_10.returnValue);
                    }
                    v1_65.LIIIII = "";
                    String v4_0 = v9_1.L;
                    if (v4_0 != null) {
                        v1_65.LIIIII = v4_0;
                    }
                    v1_65.LIIIIZ = v9_1.LB;
                } else {
                    v5_3 = new android.util.Pair(v9_4, Boolean.valueOf(v1_65.LIIIIZ));
                }
                if ((!v0_29.LCCII.LBL()) || ((((Boolean) v5_3.second).booleanValue()) || (android.text.TextUtils.isEmpty(((CharSequence) v5_3.first))))) {
                    v0_29.ag_().LFF.L("ADID unavailable to retrieve Deferred Deep Link. Skipping");
                    return;
                } else {
                    X.3PS.L(v0_29.LIIIIZZ);
                    String v1_15 = v0_29.LIIIIZZ;
                    v1_15.LCI();
                    X.3Rf v6_2 = ((android.net.ConnectivityManager) v1_15.LIIII.L.getSystemService("connectivity"));
                    android.net.NetworkInfo v7_0 = 0;
                    if (v6_2 != null) {
                        try {
                            System.nanoTime();
                        } catch (Exception) {
                            if (v7_0 != null) {
                                if (v7_0.isConnected()) {
                                    X.3PS.L(v0_29.LIIII);
                                    X.3Rf v6_3 = v0_29.LIIII;
                                    v0_29.LCCII();
                                    String v9_3 = ((String) v5_3.first);
                                    X.3PS.L(v0_29.LII);
                                    long v10_2 = (v0_29.LII.LFLL.L() + -1);
                                    try {
                                        X.3D5.L(v9_3);
                                        X.3D5.L(v2_2);
                                        java.net.URL v5_5 = new Object[4];
                                        android.net.NetworkInfo v7_1 = new Object[2];
                                        v7_1[0] = Long.valueOf(68000);
                                        v7_1[1] = Integer.valueOf(v6_3.LCC());
                                        v5_5[0] = String.format("v%s.%s", v7_1);
                                        v5_5[1] = v9_3;
                                        v5_5[2] = v2_2;
                                        v5_5[3] = Long.valueOf(v10_2);
                                        String v4_7 = String.format("https://www.googleadservices.com/pagead/conversion/app/deeplink?id_type=adid&sdk_version=%s&rdid=%s&bundleid=%s&retry=%s", v5_5);
                                    } catch (String v1_52) {
                                        v6_3.LIIII.ag_().LBL.L("Failed to create BOW URL for Deferred Deep Link. exception", v1_52.getMessage());
                                        return;
                                    } catch (String v1_52) {
                                        v6_3.LIIII.ag_().LBL.L("Failed to create BOW URL for Deferred Deep Link. exception", v1_52.getMessage());
                                        return;
                                    }
                                    if (v2_2.equals(v6_3.LIIII.LCCII.LC("debug.deferred.deeplink"))) {
                                        v4_7 = v4_7.concat("&ddl_test=1");
                                    }
                                    java.net.URL v5_7 = new java.net.URL(v4_7);
                                    X.3PS.L(v0_29.LIIIIZZ);
                                    String v4_8 = v0_29.LIIIIZZ;
                                    String v3_10 = new X.3PQ(v0_29);
                                    v4_8.ac_();
                                    v4_8.LCI();
                                    X.3D5.L(v5_7);
                                    X.3D5.L(v3_10);
                                    v4_8.LIIII.ah_().L(new X.3QP(v4_8, v2_2, v5_7, v3_10));
                                    return;
                                }
                            }
                        }
                        if (X.5uL.L()) {
                            if ((X.75K.L()) || (X.5uK.LBL())) {
                                if (X.5uV.L()) {
                                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                                        X.5uC.L = X.3PS.L(v6_2);
                                        v7_0 = X.5uC.L;
                                    } else {
                                        if (X.5uO.L) {
                                            X.5uL.L("cm_net_info", X.3PS.L(v6_2).toString(), X.5uC.L.toString());
                                        }
                                        v7_0 = X.5uC.L;
                                    }
                                } else {
                                    X.5uC.L = 0;
                                    v7_0 = X.3PS.L(v6_2);
                                }
                            } else {
                                v7_0 = X.3PS.L(v6_2);
                            }
                        } else {
                            v7_0 = X.3PS.L(v6_2);
                        }
                    }
                    v0_29.ag_().LCCII.L("Network is not available for Deferred Deep Link request. Skipping");
                    return;
                }
            } else {
                v5_0.LIIII.ag_().LCCII.L("Permanently failed to retrieve Deferred Deep Link. Reached maximum retries.");
                v5_0.LIIII.LF().LFI.L(1);
                return;
            }
        }
    }


}