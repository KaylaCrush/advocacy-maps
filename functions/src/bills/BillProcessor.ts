import { QuerySnapshot } from "@google-cloud/firestore"
import { runWith } from "firebase-functions"
import { Runtype } from "runtypes"
import { City } from "../cities/types"
import { Committee } from "../committees/types"
import { DocUpdate } from "../common"
import { db } from "../firebase"
import * as api from "../malegislature"
import { Member } from "../members/types"
import { Bill } from "./types"

export type BillUpdates = Map<string, DocUpdate<Bill>>

/** Base class for jobs that need to process all bills. */
export default abstract class BillProcessor {
  protected bills!: any[]
  protected billIds!: string[]
  protected committees!: Committee[]
  protected members!: Member[]
  protected cities!: City[]

  static pubsub(
    Processor: { new (args?: any): BillProcessor },
    topic: string,
    timeoutSeconds = 120
  ) {
    return runWith({ timeoutSeconds })
      .pubsub.topic(topic)
      .onPublish(async message => {
        if (message.json.run !== true)
          throw Error('Expected { "run": true } message')
        await new Processor(message.json).run()
      })
  }

  static scheduled(
    Processor: { new (): BillProcessor },
    schedule = "every 24 hours",
    timeoutSeconds = 120
  ) {
    return runWith({ timeoutSeconds })
      .pubsub.schedule(schedule)
      .onRun(() => new Processor().run())
  }

  private async run() {
    await this.readEntities()
    await this.process()
  }

  /** The fields to retrieve for each bill, useful to exclude the bill text in
   * particular. */
  protected get billFields(): string[] {
    return []
  }

  abstract process(): Promise<void>

  billPath(id?: string) {
    return `/generalCourts/${api.currentGeneralCourt}/bills${
      id ? `/${id}` : ""
    }`
  }

  protected async writeBills(updates: BillUpdates) {
    const validIds = new Set(this.billIds)
    const writer = db.bulkWriter()
    updates.forEach((update, id) => {
      if (validIds.has(id))
        writer.set(db.doc(this.billPath(id)), update, { merge: true })
    })
    await writer.close()
  }

  private async readEntities() {
    this.bills = await db
      .collection(this.billPath())
      .select(...this.billFields)
      .get()
      .then(snap => snap.docs.map(d => d.data()))
    this.billIds = this.bills.map(b => b.id)
    this.cities = await db
      .collection(`/generalCourts/${api.currentGeneralCourt}/cities`)
      .get()
      .then(this.load(City))
    this.committees = await db
      .collection(`/generalCourts/${api.currentGeneralCourt}/committees`)
      .get()
      .then(this.load(Committee))
    this.members = await db
      .collection(`/generalCourts/${api.currentGeneralCourt}/members`)
      .get()
      .then(this.load(Member))
  }

  protected load<T extends { id: string }>(Entity: Runtype<T>) {
    return (snap: QuerySnapshot) => snap.docs.map(d => Entity.check(d.data()))
  }
}
