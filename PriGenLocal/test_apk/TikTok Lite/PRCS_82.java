/*Application Package Name: com.tiktok.lite.go
class PRCS_82 {
/**
X.3G3;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yz1cEJOnFpNPfG57TP3DlRLqw==");
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
X.3G3;LB()Z
*/

    public final boolean LB()
    {
        X.37f.LB();
        this.LFI();
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) this.LB.L.getSystemService("connectivity"));
        try {
            android.net.NetworkInfo v0_11;
            System.nanoTime();
        } catch (Exception) {
            this.LB("No network connectivity");
            return 0;
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.3G3.L(v3_1);
                        v0_11 = X.5uC.L;
                        if ((v0_11 == null) || (!v0_11.isConnected())) {
                            this.LB("No network connectivity");
                            return 0;
                        } else {
                            return 1;
                        }
                    } else {
                        if (X.5uO.L) {
                            X.5uL.L("cm_net_info", X.3G3.L(v3_1).toString(), X.5uC.L.toString());
                        }
                        v0_11 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v0_11 = X.3G3.L(v3_1);
                }
            } else {
                v0_11 = X.3G3.L(v3_1);
            }
        } else {
            v0_11 = X.3G3.L(v3_1);
        }
    }

/**
X.3Gk;LICI()Z
*/

    private final boolean LICI()
    {
        X.37f.LB();
        void v6 = this;
        this.LFI();
        this.LB("Dispatching a batch of local hits");
        java.net.MalformedURLException v1_46 = this.LCI.LB();
        boolean vtmp2 = this.LCC.LB();
        if ((v1_46 != null) || (vtmp2)) {
            String v8_1 = new java.util.ArrayList();
            long v2 = 0;
            try {
                while(true) {
                    this.LC.LB();
                    v8_1.clear();
                    try {
                        this.LC.LBL();
                        this.LC.LC();
                    } catch (int v0_128) {
                        this.LCC("Failed to commit local dispatch transaction", v0_128);
                        this.LIIII();
                        return 0;
                    }
                }
                try {
                    this.LC.LBL();
                    this.LC.LC();
                    return 0;
                } catch (int v0_131) {
                    this.LCC("Failed to commit local dispatch transaction", v0_131);
                    this.LIIII();
                    return 0;
                }
            } catch (java.net.MalformedURLException v1_45) {
                try {
                    v6.LC.LBL();
                    v6.LC.LC();
                    throw v1_45;
                } catch (int v0_175) {
                    v6.LCC("Failed to commit local dispatch transaction", v0_175);
                    v6.LIIII();
                    return 0;
                }
            }
            java.io.IOException v7_5 = this.LC.L(((long) Math.max(X.3Fl.LCCII(), X.3Fl.LCI())));
            if (!v7_5.isEmpty()) {
                this.L("Hits loaded from store. count", Integer.valueOf(v7_5.size()));
                X.3Fw v10_0 = v7_5.iterator();
                while (v10_0.hasNext()) {
                    if (((X.3Fw) v10_0.next()).LBL == v2) {
                        this.LC("Database contains successfully uploaded hit", Long.valueOf(v2), Integer.valueOf(v7_5.size()));
                        v6 = this.LIIII();
                        try {
                            v6.LC.LBL();
                            v6.LC.LC();
                            return 0;
                        } catch (int v0_170) {
                            v6.LCC("Failed to commit local dispatch transaction", v0_170);
                            v6.LIIII();
                            return 0;
                        }
                    }
                }
                if (this.LCI.LB()) {
                    this.LB("Service connected, sending hits to the service");
                    while (!v7_5.isEmpty()) {
                        X.3Fw v10_2 = ((X.3Fw) v7_5.get(0));
                        if (!this.LCI.L(v10_2)) {
                            break;
                        }
                        v2 = Math.max(v2, v10_2.LBL);
                        v7_5.remove(v10_2);
                        this.LB("Hit sent do device AnalyticsService for delivery", v10_2);
                        try {
                            this.LC.LB(v10_2.LBL);
                            v8_1.add(Long.valueOf(v10_2.LBL));
                        } catch (java.net.MalformedURLException v1_42) {
                            this.LCC("Failed to remove hit that was send for delivery", v1_42);
                            v6 = this.LIIII();
                            try {
                                v6.LC.LBL();
                                v6.LC.LC();
                                return 0;
                            } catch (int v0_161) {
                                v6.LCC("Failed to commit local dispatch transaction", v0_161);
                                v6.LIIII();
                                return 0;
                            }
                        }
                    }
                }
                if (this.LCC.LB()) {
                    java.util.List v9_0;
                    int v16_0;
                    X.3Fw v10_3 = this.LCC;
                    X.37f.LB();
                    v10_3.LFI();
                    X.3D5.L(v7_5);
                    if ((v10_3.LB.LC.LFFFF().isEmpty()) || (!v10_3.LC.L((((long) ((Integer) X.3Fr.LIIIIZ.L).intValue()) * 1000)))) {
                        v9_0 = 0;
                        v16_0 = 0;
                    } else {
                        java.net.MalformedURLException v1_0;
                        java.net.MalformedURLException v1_48 = ((String) X.3Fr.LI.L);
                        if (!"BATCH_BY_SESSION".equalsIgnoreCase(v1_48)) {
                            if (!"BATCH_BY_TIME".equalsIgnoreCase(v1_48)) {
                                if (!"BATCH_BY_BRUTE_FORCE".equalsIgnoreCase(v1_48)) {
                                    if (!"BATCH_BY_COUNT".equalsIgnoreCase(v1_48)) {
                                        if (!"BATCH_BY_SIZE".equalsIgnoreCase(v1_48)) {
                                            v1_0 = X.3Fb.zzya;
                                        } else {
                                            v1_0 = X.3Fb.LC;
                                        }
                                    } else {
                                        v1_0 = X.3Fb.zzye;
                                    }
                                } else {
                                    v1_0 = X.3Fb.LBL;
                                }
                            } else {
                                v1_0 = X.3Fb.LB;
                            }
                        } else {
                            v1_0 = X.3Fb.L;
                        }
                        if (v1_0 == X.3Fb.zzya) {
                            v9_0 = 0;
                        } else {
                            v9_0 = 1;
                        }
                        java.net.MalformedURLException v1_3;
                        if (!"GZIP".equalsIgnoreCase(((String) X.3Fr.LICI.L))) {
                            v1_3 = X.3Fh.L;
                        } else {
                            v1_3 = X.3Fh.zzyl;
                        }
                        if (v1_3 != X.3Fh.zzyl) {
                        } else {
                            v16_0 = 1;
                        }
                    }
                    java.util.List v9_2;
                    if (v9_0 == null) {
                        v9_2 = new java.util.ArrayList(v7_5.size());
                        int v16_1 = v7_5.iterator();
                        while (v16_1.hasNext()) {
                            X.3Fw v12_1 = ((X.3Fw) v16_1.next());
                            X.3D5.L(v12_1);
                            String v15_0 = v10_3.L(v12_1, (v12_1.LCCII ^ 1));
                            if (v15_0 != null) {
                                if (v15_0.length() > ((Integer) X.3Fr.LFLL.L).intValue()) {
                                    int v0_21 = v10_3.L(v12_1, 0);
                                    if (v0_21 != 0) {
                                        byte[] v13_0 = v0_21.getBytes();
                                        if (v13_0.length <= ((Integer) X.3Fr.LIII.L).intValue()) {
                                            java.net.MalformedURLException v1_9;
                                            if (!v12_1.LCCII) {
                                                java.io.IOException v7_0 = String.valueOf(X.3Fl.LF());
                                                java.net.MalformedURLException v1_7 = String.valueOf(X.3Fl.LFF());
                                                if (v1_7.length() == 0) {
                                                    v1_9 = new String(v7_0);
                                                } else {
                                                    v1_9 = v7_0.concat(v1_7);
                                                }
                                            } else {
                                                java.io.IOException v7_1 = String.valueOf(X.3Fl.LD());
                                                java.net.MalformedURLException v1_10 = String.valueOf(X.3Fl.LFF());
                                                if (v1_10.length() == 0) {
                                                    v1_9 = new String(v7_1);
                                                } else {
                                                    v1_9 = v7_1.concat(v1_10);
                                                }
                                            }
                                            if (X.3G3.L(v10_3, new java.net.URL(v1_9), v13_0) != 200) {
                                                break;
                                            }
                                        } else {
                                            v10_3.LB.L().L(v12_1, "Hit payload exceeds size limit");
                                        }
                                    } else {
                                        v10_3.LB.L().L(v12_1, "Error formatting hit for POST upload");
                                    }
                                } else {
                                    java.net.MalformedURLException v1_18;
                                    if (!v12_1.LCCII) {
                                        byte[] v13_1 = X.3Fl.LF();
                                        java.io.IOException v7_2 = X.3Fl.LFF();
                                        int v0_53 = new StringBuilder((((String.valueOf(v13_1).length() + 1) + String.valueOf(v7_2).length()) + String.valueOf(v15_0).length()));
                                        v0_53.append(v13_1);
                                        v0_53.append(v7_2);
                                        v0_53.append("?");
                                        v0_53.append(v15_0);
                                        v1_18 = v0_53.toString();
                                    } else {
                                        byte[] v13_2 = X.3Fl.LD();
                                        java.io.IOException v7_3 = X.3Fl.LFF();
                                        int v0_62 = new StringBuilder((((String.valueOf(v13_2).length() + 1) + String.valueOf(v7_3).length()) + String.valueOf(v15_0).length()));
                                        v0_62.append(v13_2);
                                        v0_62.append(v7_3);
                                        v0_62.append("?");
                                        v0_62.append(v15_0);
                                        v1_18 = v0_62.toString();
                                    }
                                    if (X.3G3.L(v10_3, new java.net.URL(v1_18)) != 200) {
                                        break;
                                    }
                                }
                            } else {
                                v10_3.LB.L().L(v12_1, "Error formatting hit for upload");
                            }
                            v9_2.add(Long.valueOf(v12_1.LBL));
                            if (v9_2.size() >= X.3Fl.LCCII()) {
                                break;
                            }
                        }
                    } else {
                        X.3D5.L((v7_5.isEmpty() ^ 1));
                        v10_3.L("Uploading batched hits. compression, count", Boolean.valueOf(v16_0), Integer.valueOf(v7_5.size()));
                        X.3Fw v12_3 = new X.3G4(v10_3);
                        v9_2 = new java.util.ArrayList();
                        String v15_1 = v7_5.iterator();
                        while (v15_1.hasNext()) {
                            byte[] v13_4 = ((X.3Fw) v15_1.next());
                            X.3D5.L(v13_4);
                            if ((v12_3.L + 1) > X.3Fl.LCI()) {
                                break;
                            }
                            int v0_83 = v12_3.LBL.L(v13_4, 0);
                            if (v0_83 != 0) {
                                java.io.IOException v7_6 = v0_83.getBytes();
                                int v14_1 = v7_6.length;
                                if (v14_1 <= X.3Fl.LBL()) {
                                    if (v12_3.LB.size() > 0) {
                                        v14_1++;
                                    }
                                    if ((v12_3.LB.size() + v14_1) > ((Integer) X.3Fr.LIIII.L).intValue()) {
                                        break;
                                    }
                                    if (v12_3.LB.size() > 0) {
                                        v12_3.LB.write(X.3G3.L);
                                    }
                                    v12_3.LB.write(v7_6);
                                    v12_3.L = (v12_3.L + 1);
                                } else {
                                    v12_3.LBL.LB.L().L(v13_4, "Hit size exceeds the maximum size limit");
                                }
                            } else {
                                v12_3.LBL.LB.L().L(v13_4, "Error formatting hit");
                            }
                            v9_2.add(Long.valueOf(v13_4.LBL));
                        }
                        if (v12_3.L != 0) {
                            int v0_100;
                            java.io.IOException v7_7 = String.valueOf(X.3Fl.LD());
                            java.net.MalformedURLException v1_30 = String.valueOf(((String) X.3Fr.LFI.L));
                            if (v1_30.length() == 0) {
                                v0_100 = new String(v7_7);
                            } else {
                                v0_100 = v7_7.concat(v1_30);
                            }
                            java.io.IOException v7_8;
                            java.net.MalformedURLException v1_32 = new java.net.URL(v0_100);
                            if (v16_0 == 0) {
                                v7_8 = X.3G3.L(v10_3, v1_32, v12_3.LB.toByteArray());
                            } else {
                                v7_8 = X.3G3.LB(v10_3, v1_32, v12_3.LB.toByteArray());
                            }
                            if (200 != v7_8) {
                                v10_3.L("Network error uploading hits. status code", Integer.valueOf(v7_8));
                                if (!v10_3.LB.LC.LFFFF().contains(Integer.valueOf(v7_8))) {
                                    v9_2 = java.util.Collections.emptyList();
                                } else {
                                    v10_3.LCC("Server instructed the client to stop batching");
                                    v10_3.LC.L();
                                }
                            } else {
                                v10_3.L("Batched upload completed. Hits batched", Integer.valueOf(v12_3.L));
                            }
                        }
                    }
                    java.io.IOException v7_9 = v9_2.iterator();
                    while (v7_9.hasNext()) {
                        v2 = Math.max(v2, ((Long) v7_9.next()).longValue());
                    }
                    try {
                        this.LC.L(v9_2);
                        v8_1.addAll(v9_2);
                    } catch (java.net.MalformedURLException v1_37) {
                        this.LCC("Failed to remove successfully uploaded hits", v1_37);
                        v6 = this.LIIII();
                        try {
                            v6.LC.LBL();
                            v6.LC.LC();
                            return 0;
                        } catch (int v0_123) {
                            v6.LCC("Failed to commit local dispatch transaction", v0_123);
                            v6.LIIII();
                            return 0;
                        }
                    }
                }
                if (!v8_1.isEmpty()) {
                }
            } else {
                this.LB("Store is empty, nothing to dispatch");
                v6 = this.LIIII();
                try {
                    v6.LC.LBL();
                    v6.LC.LC();
                    return 0;
                } catch (int v0_181) {
                    v6.LCC("Failed to commit local dispatch transaction", v0_181);
                    v6.LIIII();
                    return 0;
                }
            }
        } else {
            this.LB("No network or service available. Will retry later");
            return 0;
        }
    }


}